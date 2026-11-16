#!/usr/bin/env python3
"""Step 1 — carry the feature diff forward to TELINDY Latest (no intermediate snapshots).

Input : WORK/feature.orig.diff (Before -> After), WORK/.port_changelog/{config,scope,answers}.json
Output: WORK/feature.diff rewritten in place (stage=latest): '-'/context from Latest, '+' = the feature
        in its Latest form, closure hunks for accepted new symbols, '# unit=...' notes per file.
Exit  : 0 done, 2 questions pending (questions.json), 1 error.

Per hunk (OVERVIEW §4 Bước 1):
  A_blk = new side of the hunk (context + '+'), feat[i] = line i is a '+' line (D1)
  locate A_blk in the Latest file -> window; align A_blk with the window (D2, on norm_line keys)
  every non-equal D2 block is classified by distance to feature lines:
     OVERLAP  touches a feature line              -> take Latest
     ADJACENT within k lines of a feature line    -> take Latest
     DISJOINT farther                             -> not ours: stays as context on both sides
  OVERLAP/ADJACENT that introduce a NEW symbol (defined in Latest, absent in target, absent in A_blk)
  -> question new_symbol. Y: take Latest + pull definitions (closure). N: keep the After form.
Whole units added by the feature (functions/macros/decls fully inside '+' runs) are taken from Latest
as a whole.
"""
import argparse
import difflib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (FileDiff, Hunk, find_units, enclosing_unit, identifiers, iter_code_files,  # noqa: E402
                    join_lines, make_hunks, norm_line, parse_diff, read_src, render_diff, set_header_note)
import locate  # noqa: E402

STATE = '.port_changelog'


# ----------------------------------------------------------------------------------------------
# small IO helpers
# ----------------------------------------------------------------------------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default


def save_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def is_modblock_line(text):
    return text.lstrip().startswith('/*#')


# ----------------------------------------------------------------------------------------------
class Carry:
    def __init__(self, work):
        self.work = work
        st = os.path.join(work, STATE)
        self.cfg = load_json(os.path.join(st, 'config.json'), {})
        self.scope = load_json(os.path.join(st, 'scope.json'), {})
        self.answers = load_json(os.path.join(st, 'answers.json'), {})
        self.latest = self.cfg['latest']
        self.target = self.cfg['target']
        self.k = int(self.cfg.get('k', 3))
        self.hi = float(self.cfg.get('hi', 0.9))
        self.lo = float(self.cfg.get('lo', 0.6))
        self.lidx = locate.DefIndex(self.latest)
        self.tidx = locate.DefIndex(self.target)
        self.questions = []
        self.out_files = {}          # latest relpath -> FileDiff
        self.notes = {}              # latest relpath -> [note lines]
        self.emitted_units = set()   # (path, name) of whole units already emitted (add/closure)
        self.closure_queue = []      # (symbol, reason)
        self._lfile_cache = {}
        self.latest_files = None

    # ---------------- helpers
    def lfile(self, rel):
        if rel not in self._lfile_cache:
            src = read_src(os.path.join(self.latest, rel))
            self._lfile_cache[rel] = (src.lines, find_units(src.text))
        return self._lfile_cache[rel]

    def map_latest_path(self, rel):
        if os.path.exists(os.path.join(self.latest, rel)):
            return rel
        if self.latest_files is None:
            self.latest_files = iter_code_files(self.latest)
        base = os.path.basename(rel)
        hits = [f for f in self.latest_files if os.path.basename(f) == base]
        return hits[0] if len(hits) == 1 else None

    def note(self, path, unit, kind, change, status, extra='', text=''):
        toks = ['unit=%s' % (unit or '-'), 'kind=%s' % (kind or '-'), 'change=%s' % change, 'status=%s' % status]
        if extra:
            toks.append(extra)
        line = '# ' + ' '.join(toks) + ((' | ' + text) if text else '')
        lst = self.notes.setdefault(path, [])
        if line not in lst:
            lst.append(line)

    def ask(self, q):
        """Register a question; return the stored answer (upper-cased) or None."""
        a = self.answers.get(q['id'])
        if a is not None:
            return str(a.get('answer', '')).strip().upper()
        if all(x['id'] != q['id'] for x in self.questions):
            self.questions.append(q)
        return None

    def rt_hint(self, unit, syms=()):
        parts = []
        for s in syms:
            src = self.scope.get('symbol_sources', {}).get(s)
            if src:
                parts.append('%s: %s %s (%s) %s.' % (s, src.get('rt'), src.get('version', ''),
                                                    src.get('date', ''), src.get('action', 'Add')))
        sus = self.scope.get('suspects', {}).get(unit)
        if sus:
            parts.append('%s được sửa bởi: %s' % (unit, ', '.join(sus)))
        return '; '.join(parts) or 'changelog không nhắc tới'

    def fd(self, path):
        if path not in self.out_files:
            self.out_files[path] = FileDiff('a/' + path, 'b/' + path, [], [])
        return self.out_files[path]

    def prev_unit_name(self, units, unit):
        prev = [u for u in units if u.end < unit.start]
        return prev[-1].name if prev else ''

    # ---------------- whole-unit emission (add / closure)
    def emit_whole_unit(self, path, unit, change, reason=''):
        key = (path, unit.name, unit.start)
        if key in self.emitted_units:
            return
        self.emitted_units.add(key)
        lines, units = self.lfile(path)
        s = unit.doc_start or unit.start
        ctx_lo = max(1, s - 3)
        before = lines[ctx_lo - 1:s - 1]
        body = lines[s - 1:unit.end]
        after = lines[unit.end:unit.end + 3]
        h = Hunk(ctx_lo, len(before) + len(after), ctx_lo, len(before) + len(body) + len(after), unit.name,
                 [(' ', x) for x in before] + [('+', x) for x in body] + [(' ', x) for x in after])
        self.fd(path).hunks.append(h)
        self.note(path, unit.name, unit.kind, change, 'TAKEN',
                  'after=%s' % (self.prev_unit_name(units, unit) or '-'), reason)
        # closure scan of the unit body
        self.scan_new_symbols(body, set(), path, unit.name, auto_reason='closure của %s' % unit.name)

    def scan_new_symbols(self, new_lines, known_ids, path, unit_name, auto_reason):
        """Queue symbols used by lines we already decided to port that target lacks."""
        for sym in sorted(identifiers('\n'.join(new_lines)) - known_ids):
            if sym == unit_name:
                continue
            if self.lidx.has(sym) and not self.tidx.has(sym):
                self.closure_queue.append((sym, auto_reason))

    def new_symbols(self, l_lines, a_ids):
        res = []
        for sym in sorted(identifiers('\n'.join(l_lines)) - a_ids):
            if self.lidx.has(sym) and not self.tidx.has(sym):
                res.append(sym)
        return res

    def run_closure(self, feature_names):
        done = set()
        while self.closure_queue:
            sym, reason = self.closure_queue.pop(0)
            if sym in done or sym in feature_names:
                continue
            done.add(sym)
            for path, unit in self.lidx.defs(sym):
                self.emit_whole_unit(path, unit, 'closure', reason)

    # ---------------- per-hunk processing
    def process_file(self, fdiff):
        rel = fdiff.path
        lpath = self.map_latest_path(rel)
        if lpath is None:
            q = {'id': 's1:%s:-:missing_unit' % rel, 'step': 1, 'kind': 'missing_unit', 'who': 'user',
                 'file': rel, 'unit': '-',
                 'message': 'File %s không có trong Latest (đã xoá/đổi tên?). Giữ nguyên dạng After của file này? (Y/N)' % rel,
                 'options': ['Y', 'N'], 'context': {}}
            a = self.ask(q)
            if a == 'Y':
                fd = FileDiff(fdiff.old_path, fdiff.new_path, [], [self.strip_modblock(h) for h in fdiff.hunks])
                fd.hunks = [h for h in fd.hunks if h is not None]
                self.out_files[rel] = fd
                self.note(rel, '-', 'file', 'mod', 'MISSING', '', 'người dùng chọn giữ dạng After')
            return
        lines, units = self.lfile(lpath)
        for h in fdiff.hunks:
            h2 = self.strip_modblock(h)
            if h2 is None:
                continue
            self.process_hunk(lpath, lines, units, h2)

    @staticmethod
    def strip_modblock(h):
        kept = [(t, x) for t, x in h.lines if not is_modblock_line(x) and t != '\\']
        if not any(t in '+-' for t, _ in kept):
            return None
        return Hunk(h.old_start, sum(1 for t, _ in kept if t in ' -'), h.new_start,
                    sum(1 for t, _ in kept if t in ' +'), h.section, kept)

    def added_units(self, h):
        """Units completely contained in contiguous '+' runs of the hunk -> [(name, kind, idx_set)]."""
        res = []
        i = 0
        L = h.lines
        while i < len(L):
            if L[i][0] != '+':
                i += 1
                continue
            j = i
            while j < len(L) and L[j][0] == '+':
                j += 1
            run = [x for _, x in L[i:j]]
            for u in find_units(join_lines(run)):
                idx = set(range(i + u.doc_start - 1, i + u.end))
                res.append((u.name, u.kind, idx, run[u.start - 1:u.end]))
            i = j
        return res

    def process_hunk(self, lpath, lines, units, h):
        # 1) whole units added by the feature -> take from Latest as a whole
        consumed = set()
        masked_latest = set()   # latest line numbers belonging to taken units
        for name, kind, idx, body in self.added_units(h):
            r = locate.find_unit(name, kind, body, self.latest, hint_files=[lpath], index=self.lidx,
                                 hi=self.hi, lo=self.lo)
            unit = r.get('unit')
            if r['status'] in ('found', 'renamed') and unit is not None:
                consumed |= idx
                upath = r['path']
                self.emit_whole_unit(upath, unit, 'add',
                                     'chức năng thêm mới — lấy nguyên bản Latest' +
                                     ('' if r['status'] == 'found' else ' (đổi tên từ %s)' % name))
                if upath == lpath:
                    masked_latest |= set(range(unit.doc_start or unit.start, unit.end + 1))
                # Latest version differs from the After version? note status
                if [norm_line(x) for x in unit.lines if norm_line(x)] != [norm_line(x) for x in body if norm_line(x)]:
                    self.note(upath, unit.name, unit.kind, 'add',
                              'CHANGED' if self.scope.get('suspects', {}).get(name) or self.is_followup(name)
                              else 'UNEXPLAINED', '', 'Latest khác After — đã lấy bản Latest')
                    # new symbols introduced after the feature inside an added unit
                    syms = self.new_symbols(unit.lines, identifiers('\n'.join(body)))
                    self.ask_new_symbols(upath, unit.name, syms, unit.lines, accept_default=True)
            else:
                q = {'id': 's1:%s:%s:missing_unit' % (lpath, name), 'step': 1, 'kind': 'missing_unit',
                     'who': 'llm' if r['status'] == 'llm' else 'user', 'file': lpath, 'unit': name,
                     'message': 'Không tìm thấy %s (chức năng thêm mới) trong Latest. Y = dùng ứng viên tốt nhất / '
                                'giữ dạng After, N = bỏ.' % name,
                     'options': ['Y', 'N'], 'context': {'candidates': r.get('candidates', [])}}
                a = self.ask(q)
                if a == 'N':
                    consumed |= idx
                elif a == 'Y' and r.get('candidates'):
                    c = r['candidates'][0]
                    cu = [u for u in self.lidx.units(c['path']) if u.name == c['name']]
                    if cu:
                        consumed |= idx
                        self.emit_whole_unit(c['path'], cu[0], 'add', 'người dùng xác nhận %s ~ %s' % (c['name'], name))
                # else: keep in the general path (After form)
        rest = [(t, x) for n, (t, x) in enumerate(h.lines) if n not in consumed]
        if not any(t in '+-' for t, _ in rest):
            return
        self.process_mod_lines(lpath, lines, units, h, rest, masked_latest)

    def is_followup(self, name):
        for e in self.scope.get('followups', []):
            for names in e.get('items', {}).values():
                if name in names:
                    return True
        return False

    def ask_new_symbols(self, path, unit, syms, l_lines, accept_default=False):
        """Ask about symbols; returns 'Y', 'N' or None. Y queues closure."""
        if not syms:
            return 'Y'
        q = {'id': 's1:%s:%s:new_symbol:%s' % (path, unit, '+'.join(syms)), 'step': 1, 'kind': 'new_symbol',
             'who': 'user', 'file': path, 'unit': unit,
             'message': '%s trong Latest dùng thêm %s (FOMULAR chưa có). Đây là phần mở rộng của %s cần merge '
                        'sang FOMULAR? (Y = merge kèm định nghĩa, N = giữ dạng cũ)' %
                        (unit, ', '.join(syms), self.scope.get('rt', 'RT')),
             'options': ['Y', 'N'],
             'context': {'snippet': '\n'.join(l_lines[:30]), 'rt_hint': self.rt_hint(unit, syms)}}
        a = self.ask(q)
        if a == 'Y':
            for s in syms:
                self.closure_queue.append((s, 'người dùng chọn Y cho %s' % unit))
        return a

    def process_mod_lines(self, lpath, lines, units, h, hl, masked_latest):
        # A_blk with feature flags; removed (B) lines anchored before A index
        A, feat, removed = [], [], {}
        for t, x in hl:
            if t == '-':
                removed.setdefault(len(A), []).append(x)
            else:
                A.append(x)
                feat.append(t == '+')
        feat_pos = {i for i, f in enumerate(feat) if f} | set(removed)

        # locate the block in Latest (whole file; masked lines of taken units excluded)
        visible = [(n, x) for n, x in enumerate(lines, 1) if n not in masked_latest]
        vis_lines = [x for _, x in visible]
        cands = locate.locate_block(A, vis_lines) if A else []
        verdict = locate.decide(cands, self.hi, self.lo) if cands else 'ask'
        section = h.section
        if verdict != 'auto':
            cand_view = [{'start': visible[c['start'] - 1][0], 'end': visible[c['end'] - 1][0],
                          'score': round(c['score'], 3), 'method': c['method'],
                          'text': '\n'.join(vis_lines[c['start'] - 1:c['end']][:15])} for c in cands[:3]]
            kind = 'llm_judge' if verdict == 'llm' else 'missing_unit'
            q = {'id': 's1:%s:%s:%s:%d' % (lpath, section or '-', kind, h.new_start), 'step': 1, 'kind': kind,
                 'who': 'llm' if verdict == 'llm' else 'user', 'file': lpath, 'unit': section or '-',
                 'message': ('Đoạn chức năng (@@ +%d) chỉ khớp một phần trong Latest. Ứng viên 1 có phải cùng logic '
                             'đã được sửa không? (Y = dùng ứng viên 1, số 1..3 = chọn ứng viên, N = giữ dạng After)'
                             if verdict == 'llm' else
                             'Không tìm thấy đoạn chức năng (@@ +%d) trong Latest (có thể đã bị gỡ/viết lại). '
                             'Y = giữ dạng After, N = bỏ đoạn này.') % h.new_start,
                 'options': ['Y', 'N', '1', '2', '3'] if verdict == 'llm' else ['Y', 'N'],
                 'context': {'block': '\n'.join(A[:30]), 'candidates': cand_view}}
            a = self.ask(q)
            pick = None
            if verdict == 'llm' and a is not None and a not in ('N',):
                pick = cands[int(a) - 1] if a.isdigit() and 0 < int(a) <= len(cands) else cands[0]
            if pick is None:
                if a == 'N' and verdict != 'llm':
                    self.note(lpath, section, '-', 'mod', 'MISSING', '', 'người dùng bỏ đoạn @@ +%d' % h.new_start)
                    return
                if a is None:
                    return   # pending
                # keep After form, anchored nowhere specific in Latest
                fd = self.fd(lpath)
                fd.hunks.append(Hunk(h.old_start, sum(1 for t, _ in hl if t in ' -'), h.new_start,
                                     sum(1 for t, _ in hl if t in ' +'), section, list(hl)))
                self.note(lpath, section, '-', 'mod', 'MISSING', '', 'giữ dạng After (không thấy trong Latest)')
                return
            best = pick
        else:
            best = cands[0]

        # window in real line numbers (+ margin so edge changes are visible)
        s_real = visible[best['start'] - 1][0]
        e_real = visible[best['end'] - 1][0]
        margin = self.k + 3
        w_lo = max(1, s_real - margin)
        w_hi = min(len(lines), e_real + margin)
        win_nums = [n for n in range(w_lo, w_hi + 1) if n not in masked_latest]
        Lw = [lines[n - 1] for n in win_nums]

        ak = [norm_line(x) for x in A]
        lk = [norm_line(x) for x in Lw]
        ops = difflib.SequenceMatcher(None, ak, lk, autojunk=False).get_opcodes()

        a_ids = identifiers('\n'.join(A))
        old_side, new_side = [], []
        classes = []
        first_eq = next((o for o in ops if o[0] == 'equal'), None)
        last_eq = next((o for o in reversed(ops) if o[0] == 'equal'), None)
        feat_latest_line = None

        def emit_removed(i):
            for x in removed.get(i, []):
                old_side.append(x)

        for tag, i1, i2, j1, j2 in ops:
            # leading/trailing Latest lines outside the aligned span: plain context
            outside = (first_eq and (i2 <= first_eq[1] and j2 <= first_eq[3]) and tag == 'insert') or \
                      (last_eq and (i1 >= last_eq[2] and j1 >= last_eq[4]) and tag == 'insert')
            if tag == 'equal':
                for di in range(i2 - i1):
                    i, j = i1 + di, j1 + di
                    emit_removed(i)
                    if feat[i]:
                        new_side.append(Lw[j])
                        if feat_latest_line is None:
                            feat_latest_line = win_nums[j]
                    else:
                        old_side.append(Lw[j])
                        new_side.append(Lw[j])
                continue
            if outside or (tag == 'insert' and (i1 == 0 or i1 == len(A)) and not (
                    (i1 - 1) in feat_pos or i1 in feat_pos)):
                for j in range(j1, j2):
                    old_side.append(Lw[j])
                    new_side.append(Lw[j])
                continue
            # classify the D2 block
            if any(feat[i] for i in range(i1, i2)) or any(i in removed for i in range(i1 + 1, i2)):
                cls = 'OVERLAP'
            else:
                lo_pos, hi_pos = (i1 - 0.5, i1 - 0.5) if tag == 'insert' else (i1, i2 - 1)
                dist = min((min(abs(p - lo_pos), abs(p - hi_pos)) for p in feat_pos), default=99)
                cls = 'ADJACENT' if dist <= self.k + 0.5 else 'DISJOINT'
            l_blk = Lw[j1:j2]
            if cls == 'DISJOINT':
                for i in range(i1, i2):
                    emit_removed(i)
                for x in l_blk:
                    old_side.append(x)
                    new_side.append(x)
                classes.append((cls, j1, None))
                continue
            syms = self.new_symbols(l_blk, a_ids)
            decision = 'Y'
            if syms:
                unit_here = enclosing_unit(units, win_nums[j1] if j1 < len(win_nums) else win_nums[-1])
                decision = self.ask_new_symbols(lpath, unit_here.name if unit_here else (section or '-'),
                                                syms, l_blk)
            classes.append((cls, j1, decision, syms))
            if decision == 'Y':
                for i in range(i1, i2):
                    emit_removed(i)
                    if not feat[i]:
                        old_side.append(A[i])
                for x in l_blk:
                    new_side.append(x)
            else:   # N or pending: keep the After form of this block
                for i in range(i1, i2):
                    emit_removed(i)
                    if feat[i]:
                        new_side.append(A[i])
                    else:
                        old_side.append(A[i])
                        new_side.append(A[i])
        emit_removed(len(A))

        # unit name for notes
        anchor_line = feat_latest_line or s_real
        u = enclosing_unit(units, anchor_line)
        uname = u.name if u else (section or '')
        ukind = u.kind if u else '-'
        if classes:
            sus = self.scope.get('suspects', {}).get(uname)
            status = 'CHANGED' if (sus or self.is_followup(uname)) else 'UNEXPLAINED'
            desc = ', '.join('%s%s%s' % (c[0], '' if c[0] == 'DISJOINT' or c[2] == 'Y' else '(N)' if c[2] == 'N' else '(?)',
                                         ('[' + '+'.join(c[3]) + ']') if len(c) > 3 and c[3] else '')
                             for c in classes)
            rt = ('rt=' + '+'.join(sus)) if sus else ''
            self.note(lpath, uname, ukind, 'mod' if u else 'toplevel', status, rt, desc)
        else:
            self.note(lpath, uname, ukind, 'mod' if u else 'toplevel', 'UNCHANGED')
        hunks = make_hunks(old_side, new_side, 3, old_offset=w_lo - 1, new_offset=w_lo - 1, section=uname)
        if not hunks:
            self.note(lpath, uname, ukind, 'mod', 'PARTIAL_REMOVED', '', 'mọi dòng chức năng đã bị gỡ trong Latest')
        self.fd(lpath).hunks.extend(hunks)

    # ---------------- main
    def run(self):
        orig = os.path.join(self.work, 'feature.orig.diff')
        with open(orig, encoding='latin-1') as f:
            gnotes, files = parse_diff(f.read())
        feature_names = set()
        for v in self.scope.get('rt_items', {}).values():
            feature_names |= set(v)
        for fdiff in files:
            self.process_file(fdiff)
        self.run_closure(feature_names)

        # assemble output: keep file order of the original diff, then closure-only files
        order = []
        for fdiff in files:
            p = self.map_latest_path(fdiff.path) or fdiff.path
            if p not in order:
                order.append(p)
        for p in sorted(set(self.out_files) | set(self.notes)):
            if p not in order:
                order.append(p)
        out = []
        for p in order:
            fd = self.out_files.get(p) or FileDiff('a/' + p, 'b/' + p, [], [])
            fd.hunks.sort(key=lambda h: h.old_start)
            fd.preamble = self.notes.get(p, [])
            if fd.hunks or fd.preamble:
                out.append(fd)
        g = [l for l in gnotes if not l.startswith('# port-changelog stage=')]
        set_header_note(g, 'rt', self.scope.get('rt') or self.cfg.get('rt') or '-')
        set_header_note(g, 'stage', 'latest' if not self.questions else 'latest-pending')
        set_header_note(g, 'latest', self.latest)
        set_header_note(g, 'target', self.target)
        with open(os.path.join(self.work, 'feature.diff'), 'w', encoding='latin-1', newline='\n') as f:
            f.write(render_diff(out, g))
        qpath = os.path.join(self.work, STATE, 'questions.json')
        save_json(qpath, {'step': 1, 'questions': self.questions})
        return 2 if self.questions else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--work', required=True)
    a = ap.parse_args(argv)
    try:
        rc = Carry(a.work).run()
    except Exception as e:   # pragma: no cover
        import traceback
        traceback.print_exc()
        print('LỖI bước 1: %s' % e, file=sys.stderr)
        return 1
    if rc == 2:
        print('Bước 1: còn câu hỏi chờ trả lời (xem .port_changelog/questions.json).')
    else:
        print('Bước 1 xong: feature.diff đã cập nhật lên Latest.')
    return rc


if __name__ == '__main__':
    sys.exit(main())
