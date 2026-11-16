#!/usr/bin/env python3
"""Step 0: read hand-written `Modification:` changelog blocks and build scope.json.

API and JSON shape: see ../references/CONTRACT.md §3 and §4.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import grep_files, parse_diff, read_src  # noqa: E402

HEAD_LIMIT = 3000   # max lines scanned for 'Modification:' before giving up (cheap head read)

_STAR_RE = re.compile(r'^/\*#\*{5,}#\*/\s*$')
_DATE_RE = re.compile(r'^(\d{4}/\d{1,2}/\d{1,2})\s+(.*)$')
_RT_RE = re.compile(r'\b(RT\d+)((?::[\w.\-]+)?)')
_VER_RE = re.compile(r'\bV\d+\.\d+(?:R\w+)?')
_ITEM_RE = re.compile(r'^([A-Z][A-Za-z]*)\.\s+(.*)$')
_IDENT_RE = re.compile(r'[A-Za-z_]\w*')


def _content(line):
    """Text between '/*#' and '#*/' (stripped), or None when the line is not a '/*#' line."""
    s = line.rstrip('\r\n')
    if not s.startswith('/*#'):
        return None
    s = s[3:]
    if s.rstrip().endswith('#*/'):
        s = s.rstrip()[:-3]
    return s.strip()


def _is_block_end(line):
    return not line.startswith('/*#') or bool(_STAR_RE.match(line.rstrip('\r\n')))


def find_mod_block(lines):
    """0-based [start, end): start = the 'Modification:' line, end = first line after the block."""
    for i, ln in enumerate(lines):
        if ln.startswith('/*#') and 'Modification:' in ln:
            j = i + 1
            while j < len(lines) and not _is_block_end(lines[j]):
                j += 1
            return i, j
    return None


def blank_mod_block(lines):
    out = list(lines)
    blk = find_mod_block(lines)
    if blk:
        for i in range(*blk):
            out[i] = ''
    return out


def norm_name(s):
    m = _IDENT_RE.search(s or '')
    return m.group(0) if m else ''


def _new_entry(date, rest, offset, raw):
    m = None
    for m in _RT_RE.finditer(rest):
        pass                                   # last RT token on the line wins
    head = rest[:m.start()] if m else rest
    v = _VER_RE.search(head)
    author = head[:v.start()] if v else head
    return {'rt': m.group(1) if m else None, 'rt_full': (m.group(1) + m.group(2)) if m else None,
            'date': date, 'author': ' '.join(author.split()), 'version': v.group(0) if v else None,
            'items': {}, 'raw': [raw], 'offset': offset}


def parse_entries(block_lines):
    """Entries newest first. Separator versions apply to the entries above them."""
    entries, pending, cur, action = [], [], None, None
    for i, ln in enumerate(block_lines):
        c = _content(ln)
        if not c or 'Modification:' in c:
            continue
        if c.startswith('---'):
            vs = _VER_RE.findall(c)
            for e in pending:
                if e['version'] is None and vs:
                    e['version'] = vs[-1]
            pending, cur, action = [], None, None
            continue
        m = _DATE_RE.match(c)
        if m:
            cur, action = _new_entry(m.group(1), m.group(2), i, ln), None
            entries.append(cur)
            pending.append(cur)
            continue
        if cur is None:
            continue
        m = _ITEM_RE.match(c)
        if m:
            action, text = m.group(1), m.group(2)
        elif action:
            text = c
        else:
            continue
        cur['raw'].append(ln)
        names = cur['items'].setdefault(action, [])
        for part in text.split(','):
            n = norm_name(part)
            if n and n not in names:
                names.append(n)
    return entries


def _read_head_block(path):
    """Read only the head of a file up to the end of its Modification block -> block lines or None."""
    block = None
    try:
        with open(path, encoding='latin-1', newline='') as f:
            for n, ln in enumerate(f):
                ln = ln.rstrip('\r\n')
                if block is None:
                    if ln.startswith('/*#') and 'Modification:' in ln:
                        block = [ln]
                    elif n >= HEAD_LIMIT:
                        return None
                elif _is_block_end(ln):
                    break
                else:
                    block.append(ln)
    except OSError:
        return None
    return block


def fingerprint_from_diff(files):
    """Entries whose header line is a '+' line inside a '/*#' run of a hunk's new side."""
    out = []
    for fd in files:
        for h in fd.hunks:
            new = [(t, x) for t, x in h.lines if t in (' ', '+')]
            k = 0
            while k < len(new):
                if not new[k][1].startswith('/*#'):
                    k += 1
                    continue
                j = k
                while j < len(new) and new[j][1].startswith('/*#'):
                    j += 1
                run = new[k:j]
                for e in parse_entries([x for _, x in run]):
                    if run[e['offset']][0] == '+' and e['rt']:
                        out.append({'file': fd.path, 'entry': e})
                k = j
    return out


def _all_names(items):
    return [n for names in items.values() for n in names]


def _pub(e, file, **extra):
    d = {'file': file}
    d.update({k: e[k] for k in ('rt', 'rt_full', 'date', 'author', 'version', 'items')})
    d.update(extra)
    return d


def _diff_unit_name(section):
    s = section.strip()
    if '(' in s:
        ids = _IDENT_RE.findall(s.split('(', 1)[0])
        return ids[-1] if ids else ''
    ids = _IDENT_RE.findall(s)
    return ids[-1] if ids else ''


def _same(a, b):
    return ' '.join((a or '').split()) == ' '.join((b or '').split())


def build_scope(diff_path, latest_dir, rt=None):
    _, files = parse_diff(read_src(diff_path).text)
    fps = fingerprint_from_diff(files)
    if rt:
        cand = [f for f in fps if f['entry']['rt'] == rt]
        cand.sort(key=lambda f: f['entry']['rt_full'] != rt)    # prefer the un-suffixed entry
    else:
        rts = sorted({f['entry']['rt'] for f in fps})
        if len(rts) != 1:
            raise ValueError('cannot pick RT from diff (found %s); pass --rt' % (rts or 'none'))
        rt, cand = rts[0], [f for f in fps if f['entry']['rt_full'] == rts[0]] or fps
    fp = dict(cand[0]['entry']) if cand else None

    # Scan Latest heads of grep hits + diff files.
    diff_paths = list(dict.fromkeys(fd.path for fd in files))
    blocks = {}
    for p in list(dict.fromkeys(grep_files(latest_dir, rt) + diff_paths)):
        full = os.path.join(latest_dir, p)
        blocks[p] = _read_head_block(full) if os.path.isfile(full) else None
    parsed = {p: parse_entries(b) for p, b in blocks.items() if b}
    if fp is None:   # fingerprint not in the diff: fall back to Latest
        for p in sorted(parsed):
            hit = [e for e in parsed[p] if e['rt_full'] == rt]
            if hit:
                fp = dict(hit[0])
                break
    if fp is None:
        raise ValueError('no changelog entry for %s in diff or Latest' % rt)

    main, warns = {}, {}
    for p, ents in parsed.items():
        same = [k for k, e in enumerate(ents) if e['rt'] == rt and e['rt_full'] == fp['rt_full']]
        exact = [k for k in same if ents[k]['date'] == fp['date'] and _same(ents[k]['author'], fp['author'])]
        if exact or same:
            main[p] = (exact or same)[0]
            if not exact:
                warns[p] = 'entry %s có trong Latest nhưng ngày/người làm khác dấu vân tay' % rt
            if fp['version'] is None:
                fp['version'] = ents[main[p]]['version']
    fp.pop('offset', None)
    rt_items = fp['items']
    rt_names = set(_all_names(rt_items))

    out_files = []
    for p in diff_paths + sorted(p for p in main if p not in diff_paths):
        exists = os.path.isfile(os.path.join(latest_dir, p))
        in_diff, has = p in diff_paths, p in main
        w = warns.get(p)
        if not exists:
            w = 'file không còn trong Latest (có thể đã đổi tên/gộp) — tìm theo nội dung'
        elif in_diff and not has:
            w = ('.h thường không có khối Modification — vẫn xử lý' if not blocks.get(p)
                 else 'không thấy entry %s trong khối Modification của Latest' % rt)
        elif has and not in_diff:
            w = 'file có entry %s trong Latest nhưng không có trong diff' % rt
        out_files.append({'path': p, 'in_diff': in_diff, 'has_entry': has, 'latest_exists': exists,
                          'warning': w})

    later, followups, suspects, sources = [], [], {}, {}
    for f in out_files:
        p = f['path']
        if p not in main:
            continue
        for k, e in enumerate(parsed[p]):
            if k == main[p]:
                continue
            touches = [n for n in _all_names(e['items']) if n in rt_names]
            if e['rt'] == rt:
                followups.append(_pub(e, p, relation='followup', touches=touches))
                continue
            if k > main[p]:
                continue                       # older than the RT entry
            rel = 'suspect' if touches else ('symbol_source' if e['items'].get('Add') else 'unrelated')
            later.append(_pub(e, p, relation=rel, touches=touches))
            for n in touches:
                suspects.setdefault(n, [])
                if e['rt'] not in suspects[n]:
                    suspects[n].append(e['rt'])
            for action, names in e['items'].items():
                for n in names:
                    old = sources.get(n)
                    if old is None or (action == 'Add' and old['action'] != 'Add'):
                        sources[n] = {'rt': e['rt'], 'version': e['version'], 'date': e['date'],
                                      'file': p, 'action': action}

    units = []
    for fd in files:
        for h in fd.hunks:
            u = _diff_unit_name(h.section)
            if u and u not in units:
                units.append(u)
    return {'rt': rt, 'fingerprint': fp, 'files': out_files, 'later_entries': later,
            'followups': followups, 'suspects': suspects, 'symbol_sources': sources,
            'rt_items': rt_items, 'diff_units': units,
            'coverage': {'missing_in_diff': [n for n in _all_names(rt_items) if n not in units],
                         'extra_in_diff': [u for u in units if u not in rt_names]}}


def insert_entry(lines, raw_entry_lines):
    blk = find_mod_block(lines)
    if not blk:
        return list(lines)
    s = blk[0] + 1
    return list(lines[:s]) + list(raw_entry_lines) + list(lines[s:])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sc = sub.add_parser('scope')
    sc.add_argument('--diff', required=True)
    sc.add_argument('--latest', required=True)
    sc.add_argument('--rt')
    sc.add_argument('--out', required=True)
    sh = sub.add_parser('show')
    sh.add_argument('file')
    a = ap.parse_args(argv)
    try:
        if a.cmd == 'scope':
            data = build_scope(a.diff, a.latest, a.rt)
            os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
            with open(a.out, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            print('scope: %s, %d file(s), %d later entr(ies)' % (data['rt'], len(data['files']),
                                                                  len(data['later_entries'])))
        else:
            lines = read_src(a.file).lines
            blk = find_mod_block(lines)
            ents = parse_entries(lines[blk[0]:blk[1]]) if blk else []
            print(json.dumps(ents, ensure_ascii=False, indent=1))
    except (OSError, ValueError) as ex:
        print('error: %s' % ex, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
