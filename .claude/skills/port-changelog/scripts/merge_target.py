#!/usr/bin/env python3
"""Step 2 of port-changelog: map feature.diff (stage=latest) onto the target tree.

Usage: merge_target.py --work W

- Recreates W/target_out/ as a fresh copy of target on every run, then applies the hunks.
- Decision per hunk follows CONTRACT §5 (AUTO / SKIP / questions).
- Writes per-file '# step2 unit=... result=...' notes into feature.diff and sets stage=merged
  when nothing is pending.
Exit codes: 0 done, 2 questions pending (questions.json), 1 error.
"""
import argparse
import difflib
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # noqa: E402
from common import norm_line, read_src, write_src, join_lines, find_units, best_unit  # noqa: E402

STATE = '.port_changelog'
STEP2_PREFIX = '# step2 '
TOPLEVEL = '-'            # carry.py writes unit=- for lines outside units
PAIR_RATIO = 0.8          # fuzzy pairing of a '-'/context line with a differing target line
RESULT_RANK = {'ASK': 5, 'USER_N': 4, 'USER_Y': 3, 'AUTO': 2, 'SKIP': 1}


# ----------------------------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------------------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')


def global_tokens(glob_notes):
    """{key: value} from '# port-changelog k=v k2=v2' lines."""
    out = {}
    for line in glob_notes:
        for tok in line[len(common.GLOBAL_NOTE):].split():
            if '=' in tok:
                k, v = tok.split('=', 1)
                out[k] = v
    return out


def parse_note(line):
    """'# unit=X kind=func change=mod after=Y | text' -> {'unit': 'X', ..., '_text': 'text'}."""
    body = line[1:].strip()
    text = ''
    if ' | ' in body:
        body, text = body.split(' | ', 1)
    d = {'_text': text.strip()}
    for tok in body.split():
        if '=' in tok:
            k, v = tok.split('=', 1)
            d[k] = v
    return d


def unit_notes(fd):
    """{unit name: note dict} of the '# unit=...' lines (step 1 notes) of one file."""
    res = {}
    for l in fd.preamble:
        if l.startswith('# unit='):
            d = parse_note(l)
            cur = res.setdefault(d.get('unit', ''), {})
            for k, v in d.items():
                if v in ('', '-'):
                    continue
                # a unit can carry several notes; a whole-unit note (add/closure) wins for 'change'
                if k == 'change' and cur.get('change') in ('add', 'closure'):
                    continue
                if k not in cur or k == 'change' and v in ('add', 'closure'):
                    cur[k] = v
    return res


def step2_notes(fd):
    res = {}
    for l in fd.preamble:
        if l.startswith(STEP2_PREFIX):
            d = parse_note('#' + l[len(STEP2_PREFIX):])
            res[d.get('unit', '')] = d
    return res


def line_key(line):
    k = norm_line(line)
    return k if k else '\x00' + line.strip()


def plain_names(name):
    return re.sub(r'[\s(\[].*$', '', name.strip())


def interpret_answer(ans):
    """('Y'|'N'|'NUM'|'TEXT', value) for one answers.json entry."""
    a = str(ans.get('answer', '')).strip()
    low = a.lower()
    if low in ('y', 'yes', 'có', 'co', 'ok', 'true'):
        return 'Y', None
    if low in ('n', 'no', 'không', 'khong', 'false', 'skip'):
        return 'N', None
    if re.fullmatch(r'\d+', a):
        return 'NUM', int(a)
    return 'TEXT', a


# ----------------------------------------------------------------------------------------------
# Hunk application
# ----------------------------------------------------------------------------------------------
def _pair_fuzzy(old_keys, win_keys, i1, i2, j1, j2, mapping):
    """Inside a 'replace' block: map old lines to target lines that differ only slightly."""
    j = j1
    for i in range(i1, i2):
        for jj in range(j, j2):
            if difflib.SequenceMatcher(None, old_keys[i], win_keys[jj], autojunk=False).ratio() >= PAIR_RATIO:
                mapping[i] = jj
                j = jj + 1
                break


def apply_at(lines, start, end, hunk):
    """Apply `hunk` to `lines` inside the 1-based inclusive window [start, end].

    Aligned context lines keep the target's own text, aligned '-' lines are dropped, '+' lines are
    inserted at their relative position; unaligned target lines in the window stay in place.
    Returns (new_lines, window_new_len).
    """
    window = lines[start - 1:end]
    old = [(tag, t) for tag, t in hunk.lines if tag in (' ', '-')]
    old_keys = [line_key(t) for _, t in old]
    win_keys = [line_key(t) for t in window]
    sm = difflib.SequenceMatcher(None, old_keys, win_keys, autojunk=False)
    mapping = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                mapping[i1 + k] = j1 + k
        elif tag == 'replace':
            _pair_fuzzy(old_keys, win_keys, i1, i2, j1, j2, mapping)
    out = []
    wj = 0
    oi = 0
    for tag, t in hunk.lines:
        if tag in (' ', '-'):
            j = mapping.get(oi)
            oi += 1
            if j is None or j < wj:
                continue
            out.extend(window[wj:j])
            if tag == ' ':
                out.append(window[j])
            wj = j + 1
        elif tag == '+':
            out.append(t)
    out.extend(window[wj:])
    return lines[:start - 1] + out + lines[end:], len(out)


def insert_new_unit(lines, block, anchor_end):
    """Insert `block` (list of lines) after 1-based line `anchor_end` (0 = top) with blank separators."""
    b = list(block)
    while b and not b[0].strip():
        b.pop(0)
    while b and not b[-1].strip():
        b.pop()
    if not b:
        return lines, 0
    ins = []
    if anchor_end > 0 and lines[anchor_end - 1].strip():
        ins.append('')
    first = anchor_end + len(ins) + 1
    ins += b
    if anchor_end < len(lines) and lines[anchor_end].strip():
        ins.append('')
    return lines[:anchor_end] + ins + lines[anchor_end:], first


# ----------------------------------------------------------------------------------------------
# Merger
# ----------------------------------------------------------------------------------------------
class Merger:
    def __init__(self, work):
        self.work = os.path.abspath(work)
        self.state = os.path.join(self.work, STATE)
        self.cfg = load_json(os.path.join(self.state, 'config.json'), None)
        if not self.cfg:
            raise SystemExit('Thiếu config.json trong %s' % self.state)
        self.latest = self.cfg['latest']
        self.target = self.cfg['target']
        self.hi = float(self.cfg.get('hi', 0.9))
        self.lo = float(self.cfg.get('lo', 0.6))
        self.scope = load_json(os.path.join(self.state, 'scope.json'), {})
        self.answers = load_json(os.path.join(self.state, 'answers.json'), {})
        self.out = os.path.join(self.work, 'target_out')
        self.questions = []
        import locate  # noqa: E402  (written in parallel; imported lazily)
        self.locate = locate
        self.tindex = locate.DefIndex(self.target)
        self.target_files = common.iter_code_files(self.target)

    # -------------------------------------------------------------------------------- questions
    def ask(self, qid, kind, who, file, unit, message, options, context):
        """Return the answer dict if answered, else register the question and return None."""
        if qid in self.answers:
            return self.answers[qid]
        self.questions.append({'id': qid, 'step': 2, 'kind': kind, 'who': who, 'file': file,
                               'unit': unit, 'message': message, 'options': options,
                               'context': context})
        return None

    def rt_hint(self, unit):
        fp = self.scope.get('fingerprint') or {}
        hint = fp.get('rt') or self.cfg.get('rt') or ''
        sus = (self.scope.get('suspects') or {}).get(unit)
        if sus:
            hint += ' (RT sau có đụng tới: %s)' % ', '.join(sus)
        return hint

    # -------------------------------------------------------------------------------- file mapping
    def map_file(self, fd, notes):
        rel = fd.path
        if os.path.isfile(os.path.join(self.target, rel)):
            return rel, 'cùng đường dẫn'
        base = os.path.basename(rel)
        same = [f for f in self.target_files if os.path.basename(f) == base]
        if len(same) == 1:
            return same[0], 'cùng tên file'
        names = [n for n in notes if n and n != TOPLEVEL] + [h.section for h in fd.hunks if h.section]
        votes = {}
        for n in dict.fromkeys(names):
            for path, _u in self.tindex.defs(n):
                votes[path] = votes.get(path, 0) + 1
        if votes:
            ranked = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))
            if len(ranked) == 1 or ranked[0][1] > ranked[1][1]:
                return ranked[0][0], 'theo định nghĩa unit'
        return None, None

    # -------------------------------------------------------------------------------- unit range
    def unit_range(self, lines, name, kind, tpath, fd_path):
        """(lo_line, hi_line, strict (lo, hi) or None, target unit name or None) for the hunk search.

        The padded range (+-3 lines) lets hunk context reach into the neighbours; the strict range
        is the unit itself (doc comment included)."""
        n = len(lines)
        if not name:
            return 1, n, None, None
        units = find_units(join_lines(lines))
        u = best_unit(units, name)
        if u is None:
            # renamed unit? ask locate (on the original target tree)
            ref = []
            lp = os.path.join(self.latest, fd_path)
            if os.path.isfile(lp):
                lu = best_unit(find_units(read_src(lp).text), name)
                ref = lu.lines if lu else []
            if ref:
                try:
                    r = self.locate.find_unit(name, kind or 'func', ref, self.target, hint_files=[tpath],
                                              index=self.tindex, hi=self.hi, lo=self.lo)
                except Exception:   # noqa: BLE001 - locate is best effort here
                    r = None
                if r and r.get('status') in ('found', 'renamed') and r.get('path') == tpath and r.get('unit'):
                    u = best_unit(units, r['unit'].name)
        if u is None:
            return 1, n, None, None
        start = u.doc_start or u.start
        return max(1, start - 3), min(n, u.end + 3), (start, u.end), u.name

    # -------------------------------------------------------------------------------- one file
    def merge_file(self, fd):
        notes = unit_notes(fd)
        results = {}           # unit -> [(result, reason)]

        def rec(unit, result, reason):
            results.setdefault(unit or TOPLEVEL, []).append((result, reason))

        units_in_diff = list(dict.fromkeys([h.section or TOPLEVEL for h in fd.hunks]))
        tpath, how = self.map_file(fd, notes)
        if tpath is None:
            qid = 's2:%s::target_file_missing' % fd.path
            a = self.ask(qid, 'target_file_missing', 'user', fd.path, '',
                         'Không tìm thấy file %s trong target. Tạo file mới từ nội dung Latest? [Y/N]' % fd.path,
                         ['Y', 'N'], {'units': units_in_diff, 'rt_hint': self.rt_hint('')})
            if a is None:
                for u in units_in_diff:
                    rec(u, 'ASK', 'chờ trả lời: thiếu file trong target')
                return results, False
            kind, _v = interpret_answer(a)
            lp = os.path.join(self.latest, fd.path)
            if kind == 'Y' and os.path.isfile(lp):
                dst = os.path.join(self.out, fd.path)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(lp, dst)
                for u in units_in_diff:
                    rec(u, 'USER_Y', 'tạo file mới từ Latest theo người dùng')
            else:
                why = 'người dùng chọn không tạo file' if kind != 'Y' else 'không có file trong Latest để tạo'
                for u in units_in_diff:
                    rec(u, 'USER_N', why)
            return results, False

        dst = os.path.join(self.out, tpath)
        src = read_src(dst)
        lines = src.lines
        changed = False
        inserted_units = set()
        per_unit_count = {}

        for h in fd.hunks:
            unit = h.section
            ukey = unit or TOPLEVEL
            per_unit_count[ukey] = per_unit_count.get(ukey, 0) + 1
            hid = 'h%d' % per_unit_count[ukey]
            note = notes.get(unit, {})
            change = note.get('change', '')
            kind = note.get('kind', '')
            minus = [t for tag, t in h.lines if tag == '-']
            plus = [t for tag, t in h.lines if tag == '+']
            ctx = [t for tag, t in h.lines if tag == ' ']
            plus_nb = [t for t in plus if norm_line(t)]
            minus_nb = [t for t in minus if norm_line(t)]
            qbase = 's2:%s:%s' % (fd.path, unit)
            snippet = '\n'.join(tag + t for tag, t in h.lines if tag != '\\')

            # ---- whole new unit (pure add) ------------------------------------------------------
            if not minus and unit and unit not in inserted_units:
                cur_units = find_units(join_lines(lines))
                plus_units = {u.name for u in find_units(join_lines(plus))}
                ukind = kind if kind in ('func', 'decl', 'macro') else None
                is_new_unit = change in ('add', 'closure') or (
                    unit in plus_units and best_unit(cur_units, unit, ukind) is None)
                if is_new_unit:
                    if best_unit(cur_units, unit, ukind) is not None:
                        rec(unit, 'SKIP', 'unit đã có trong target')
                        continue
                    elsewhere = [p for p, u in self.tindex.defs(unit)
                                 if p != tpath and (ukind is None or u.kind == ukind)]
                    if elsewhere:
                        rec(unit, 'SKIP', 'unit đã có trong target (%s)' % elsewhere[0])
                        continue
                    after = note.get('after')
                    anchor = best_unit(cur_units, after) if after else None
                    if anchor is not None:
                        pos, where = anchor.end, 'sau %s' % anchor.name
                    elif cur_units:
                        pos, where = max(u.end for u in cur_units), 'sau unit cuối file'
                    else:
                        pos, where = len(lines), 'cuối file'
                    lines, at = insert_new_unit(lines, plus, pos)
                    inserted_units.add(unit)
                    changed = True
                    rec(unit, 'AUTO', 'thêm unit mới %s (L%d)' % (where, at))
                    continue

            lo_l, hi_l, strict, tunit = self.unit_range(lines, unit, kind, tpath, fd.path)
            rng = lines[lo_l - 1:hi_l]

            # ---- SKIP: '+' side already present -------------------------------------------------
            if plus_nb:
                if all(self.locate.line_in(t, rng) for t in plus_nb):
                    old_c = self.locate.locate_block(h.old_lines(), lines, lo_l, hi_l) if minus_nb else []
                    new_c = self.locate.locate_block(h.new_lines(), lines, lo_l, hi_l)
                    old_auto = bool(minus_nb) and self.locate.decide(old_c, self.hi, self.lo) == 'auto'
                    if not old_auto or (new_c and new_c[0]['score'] >= self.hi):
                        rec(unit, 'SKIP', 'target đã có các dòng +')
                        continue
            elif minus_nb and not any(self.locate.line_in(t, rng) for t in minus_nb):
                rec(unit, 'SKIP', 'các dòng - đã không còn trong target')
                continue

            # ---- pure add without any anchor ----------------------------------------------------
            old_side = h.old_lines()
            if not any(norm_line(t) for t in old_side):
                qid = qbase + ':insert_point:' + hid
                a = self.ask(qid, 'insert_point', 'user', fd.path, unit,
                             'Không có dòng ngữ cảnh để biết chèn đoạn mới của %s ở đâu. '
                             'Chèn ngay sau %s? [Y/N]' % (ukey, tunit or 'cuối file'),
                             ['Y', 'N'], {'snippet': snippet, 'candidates': [], 'rt_hint': self.rt_hint(unit)})
                if a is None:
                    rec(unit, 'ASK', 'chờ trả lời: không có vị trí chèn')
                    continue
                k, _v = interpret_answer(a)
                if k == 'Y':
                    u = best_unit(find_units(join_lines(lines)), tunit) if tunit else None
                    pos = u.end if u else len(lines)
                    lines, at = insert_new_unit(lines, plus, pos)
                    changed = True
                    rec(unit, 'USER_Y', 'người dùng đồng ý chèn tại L%d' % at)
                else:
                    rec(unit, 'USER_N', 'người dùng chọn bỏ qua')
                continue

            # ---- locate the '-' side --------------------------------------------------------------
            cands = self.locate.locate_block(old_side, lines, lo_l, hi_l)
            dec = self.locate.decide(cands, self.hi, self.lo)
            if dec != 'auto' and strict:
                # prefer candidates inside the unit itself: the padding must not offer the
                # neighbouring unit's lines as an answer to a question about this unit
                s_c = self.locate.locate_block(old_side, lines, strict[0], strict[1])
                s_dec = self.locate.decide(s_c, self.hi, self.lo)
                if s_c and (s_dec == 'auto' or not cands or s_c[0]['score'] >= cands[0]['score'] - 0.05):
                    cands, dec = s_c, s_dec
            if dec == 'auto':
                c = cands[0]
                lines, _n = apply_at(lines, c['start'], c['end'], h)
                changed = True
                rec(unit, 'AUTO', 'áp dụng tự động tại L%d-%d (giống %d%%)'
                    % (c['start'], c['end'], round(c['score'] * 100)))
                continue

            top = [c for c in cands if c['score'] > 0][:3]
            ambiguous = (len(top) >= 2 and top[1]['score'] >= self.lo
                         and top[0]['score'] - top[1]['score'] < 0.1)
            cand_ctx = [{'n': i + 1, 'start': c['start'], 'end': c['end'], 'score': round(c['score'], 3),
                         'method': c.get('method'), 'text': '\n'.join(lines[c['start'] - 1:c['end']])}
                        for i, c in enumerate(top)]
            context = {'snippet': snippet, 'candidates': cand_ctx, 'rt_hint': self.rt_hint(unit),
                       'target_file': tpath}
            if ambiguous:
                qkind, who = 'target_ambiguous', 'user'
                msg = ('%s: đoạn cần sửa khớp nhiều chỗ trong target %s. Áp dụng ở chỗ nào? '
                       '(số 1-%d, Y = chỗ tốt nhất, N = bỏ qua)' % (ukey, tpath, len(top)))
            elif dec == 'llm':
                qkind, who = 'llm_judge', 'llm'
                msg = ('%s: target %s chỉ giống một phần (%d%%). Có phải cùng đoạn code không? '
                       '(Y = áp dụng ở ứng viên 1, số = ứng viên khác, N = bỏ qua)'
                       % (ukey, tpath, round(top[0]['score'] * 100)))
            else:
                qkind, who = 'target_mismatch', 'user'
                if top:
                    msg = ('%s: target %s đã khác, không thấy cả phía - lẫn phía +. Áp dụng ở ứng viên '
                           'gần nhất? (Y / số 1-%d / N = bỏ qua, sửa tay)' % (ukey, tpath, len(top)))
                else:
                    msg = ('%s: target %s đã khác, không tìm được vị trí nào. Trả lời N để bỏ qua '
                           '(cần sửa tay).' % (ukey, tpath))
            opts = (['Y', 'N'] + [str(i + 1) for i in range(len(top))]) if top else ['N']
            a = self.ask('%s:%s:%s' % (qbase, qkind, hid), qkind, who, fd.path, unit, msg, opts, context)
            if a is None:
                rec(unit, 'ASK', 'chờ trả lời: %s' % qkind)
                continue
            k, v = interpret_answer(a)
            by = a.get('by', 'user')
            idx = 0 if k == 'Y' else (v - 1 if k == 'NUM' else None)
            if idx is not None and 0 <= idx < len(top):
                c = top[idx]
                lines, _n = apply_at(lines, c['start'], c['end'], h)
                changed = True
                rec(unit, 'USER_Y', '%s chọn áp dụng tại L%d-%d (ứng viên %d)'
                    % ('LLM' if by == 'llm' else 'người dùng', c['start'], c['end'], idx + 1))
            elif k == 'TEXT':
                rec(unit, 'USER_N', 'trả lời không phải Y/N/số (%s) — coi như bỏ qua' % v[:40])
            elif k in ('Y', 'NUM'):
                rec(unit, 'USER_N', 'không có ứng viên số %s — coi như bỏ qua' % (v if v else 1))
            else:
                rec(unit, 'USER_N', '%s chọn bỏ qua' % ('LLM' if by == 'llm' else 'người dùng'))

        if changed:
            lines = self.add_changelog(lines)
            write_src(dst, join_lines(lines, src.final_newline), src.eol, src.final_newline)
        return results, changed

    def add_changelog(self, lines):
        fp = self.scope.get('fingerprint') or {}
        raw = fp.get('raw') or []
        if not raw:
            return lines
        import changelog  # noqa: E402
        if changelog.find_mod_block(lines) is None:
            return lines
        have = {l.strip() for l in lines}
        if any(r.strip() and r.strip() in have for r in raw[:1]):
            return lines   # entry already present -> never insert twice
        return changelog.insert_entry(lines, list(raw))

    # -------------------------------------------------------------------------------- main
    def run(self):
        diff_path = os.path.join(self.work, 'feature.diff')
        dsrc = read_src(diff_path)
        glob, files = common.parse_diff(dsrc.text)
        stage = global_tokens(glob).get('stage')
        if stage not in ('latest', 'merged'):
            print('Lỗi: feature.diff đang ở stage=%s, cần chạy bước 1 trước (stage=latest).' % stage)
            return 1
        if os.path.exists(self.out):
            shutil.rmtree(self.out)
        shutil.copytree(self.target, self.out, symlinks=True)

        summary = {}
        for fd in files:
            results, _changed = self.merge_file(fd)
            # replace step2 notes of this file
            new_notes = []
            for unit, lst in results.items():
                res = max((r for r, _ in lst), key=lambda r: RESULT_RANK[r])
                reasons = '; '.join(dict.fromkeys(why for _, why in lst))
                note = '%sunit=%s result=%s | %s' % (STEP2_PREFIX, unit, res, reasons)
                # feature.diff is handled as latin-1 (code bytes kept 1:1); store the Vietnamese
                # note text as UTF-8 bytes so the file stays readable as UTF-8 for these lines
                new_notes.append(note.encode('utf-8').decode('latin-1'))
                summary[res] = summary.get(res, 0) + 1
            pre = [l for l in fd.preamble if not l.startswith(STEP2_PREFIX)]
            last_unit = max([i for i, l in enumerate(pre) if l.startswith('# unit=')], default=None)
            if last_unit is None:
                last_note = max([i for i, l in enumerate(pre) if l.startswith('#')], default=-1)
                ins = last_note + 1
            else:
                ins = last_unit + 1
            fd.preamble = pre[:ins] + new_notes + pre[ins:]

        pending = len(self.questions)
        glob = list(glob)
        common.set_header_note(glob, 'stage', 'latest' if pending else 'merged')
        write_src(diff_path, common.render_diff(files, glob).rstrip('\n'), dsrc.eol, True)
        save_json(os.path.join(self.state, 'questions.json'), {'step': 2, 'questions': self.questions})

        print('Bước 2: ' + (', '.join('%s=%d' % kv for kv in sorted(summary.items())) or 'không có hunk'))
        print('Kết quả ghi vào: %s' % self.out)
        if pending:
            print('Còn %d câu hỏi chờ trả lời (xem %s/questions.json).' % (pending, STATE))
            return 2
        print('Xong, feature.diff đã chuyển sang stage=merged.')
        return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='port-changelog step 2: merge vào bản copy target')
    ap.add_argument('--work', required=True)
    args = ap.parse_args(argv)
    try:
        return Merger(args.work).run()
    except SystemExit as e:
        if isinstance(e.code, str):
            print('Lỗi: ' + e.code)
            return 1
        raise
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print('Lỗi: %s' % e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
