#!/usr/bin/env python3
"""Rename-invariant similarity of one reference symbol against every top-level block of a tree (recipe R17).

No embeddings, no network, standard library only. Deterministic.

Usage:
  python3 -I similarity.py --ref-file REQ-A/src/x.c --ref-name TonerSave_GetLevel --root SOURCE_ROOT
  python3 -I similarity.py --ref-file REQ-A/src/x.c --ref-lines 40-77 --root SOURCE_ROOT \
          [--feature-ids _work/B_feature_ids.txt] [--top 5] [--min-tokens 15] [--json]

Signals reported per candidate (never blended into one number):
  blind    containment of the reference's 4-token shingles in the candidate after replacing EVERY
           non-keyword identifier by $I (literals, keywords, operators kept) -> survives any rename
  named    same, but only identifiers listed in --feature-ids become $F, others stay literal
           (stricter; only when --feature-ids is given)
  size     candidate tokens / reference tokens (>> 1 may mean MERGED or grown by extensions)
  lits     shared literals / reference literals (numbers, strings, chars)
  calls    shared callee names / reference callee names (unchanged external APIs survive renames)
  sig      '=' same parameter count and same return/storage tokens, '~' same parameter count, '!' different
Containment (not Jaccard) is used so that a function that grew after the request is not penalised.
"""
import argparse
import json
import os
import re
import sys

CODE_EXT = {'.c', '.h', '.cc', '.cpp', '.cxx', '.hpp', '.hh', '.hxx', '.inc', '.ipp'}
SKIP_DIRS = {'.git', 'build', 'out', '_work'}

KEYWORDS = set("""
auto break case char const continue default do double else enum extern float for goto if inline int long
register restrict return short signed sizeof static struct switch typedef union unsigned void volatile while
_Bool bool true false NULL nullptr class namespace template typename public private protected virtual override
new delete this operator using try catch throw constexpr noexcept static_cast const_cast reinterpret_cast
dynamic_cast explicit friend mutable
int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t size_t ssize_t uintptr_t intptr_t
BOOL BYTE WORD DWORD UCHAR USHORT ULONG UINT INT CHAR VOID TRUE FALSE
""".split())
CONTROL = {'if', 'for', 'while', 'switch', 'return', 'sizeof', 'case', 'do', 'else'}

TOKEN_RE = re.compile(r"""
    (?P<ws>\s+)
  | (?P<lcom>//[^\n]*)
  | (?P<bcom>/\*.*?\*/)
  | (?P<str>"(?:\\.|[^"\\\n])*")
  | (?P<chr>'(?:\\.|[^'\\\n])+')
  | (?P<num>0[xX][0-9A-Fa-f]+[uUlL]*|\d+\.\d*(?:[eE][+-]?\d+)?[fFlL]?|\.\d+(?:[eE][+-]?\d+)?[fFlL]?|\d+(?:[eE][+-]?\d+)?[uUlLfF]*)
  | (?P<id>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<op>->|\+\+|--|<<=|>>=|<<|>>|<=|>=|==|!=|&&|\|\||\+=|-=|\*=|/=|%=|&=|\|=|\^=|::|\.\.\.|[^\sA-Za-z0-9_])
""", re.S | re.X)


def read_text(path):
    with open(path, 'rb') as f:
        data = f.read()
    # latin-1 maps every byte 1:1, so Shift-JIS / UTF-8 literals still compare byte-for-byte
    return data.decode('latin-1').replace('\r\n', '\n').replace('\r', '\n')


def blank_preprocessor(text):
    """Replace preprocessor lines (and their continuations) by empty lines, keeping line numbers."""
    out, cont = [], False
    for line in text.split('\n'):
        if cont or line.lstrip().startswith('#'):
            cont = line.rstrip().endswith('\\')
            out.append('')
        else:
            out.append(line)
    return '\n'.join(out)


def tokenize(text):
    """Return list of (kind, value, line)."""
    toks, line, pos = [], 1, 0
    for m in TOKEN_RE.finditer(text):
        kind, val = m.lastgroup, m.group()
        if kind not in ('ws', 'lcom', 'bcom'):
            toks.append((kind, val, line))
        line += val.count('\n')
    return toks


def blocks(toks):
    """Top-level brace blocks: functions, tables (= {), struct/enum/union bodies."""
    res, depth, i, n = [], 0, 0, len(toks)
    start_idx = 0  # index of first token of the current top-level statement
    while i < n:
        k, v, ln = toks[i]
        if depth == 0 and v == ';':
            start_idx = i + 1
        elif v == '{':
            if depth == 0:
                head = toks[start_idx:i]
                open_i = i
                depth = 1
                i += 1
                while i < n and depth:
                    if toks[i][1] == '{':
                        depth += 1
                    elif toks[i][1] == '}':
                        depth -= 1
                    i += 1
                end_i = i - 1
                # tables: "... = { ... };" -> include up to ';'
                info = classify(head)
                if info:
                    name, kind = info
                    res.append({'name': name, 'kind': kind,
                                'start': head[0][2] if head else toks[open_i][2],
                                'end': toks[end_i][2],
                                'head': head, 'body': toks[open_i:end_i + 1]})
                if kind_is_statement(head):
                    tail_start = i
                    while i < n and toks[i][1] != ';' and toks[i][1] != '{':
                        i += 1
                    if info and info[0] == '<anon>' and res:
                        # typedef struct { ... } Name;  -> take Name
                        ids = [t[1] for t in toks[tail_start:i] if t[0] == 'id']
                        if ids:
                            res[-1]['name'] = ids[-1]
                    if i < n and toks[i][1] == ';':
                        i += 1
                start_idx = i
                continue
            depth += 1
        elif v == '}':
            depth = max(0, depth - 1)
            if depth == 0:
                start_idx = i + 1
        i += 1
    return res


def kind_is_statement(head):
    vals = [t[1] for t in head]
    return '=' in vals or (vals and vals[0] in ('struct', 'enum', 'union', 'typedef', 'class'))


def classify(head):
    vals = [t[1] for t in head]
    if not vals:
        return None
    if vals[0] in ('extern',) and len(vals) > 1 and vals[1].startswith('"'):
        return None  # extern "C" { ... }
    if vals[0] == 'namespace':
        return None
    if '=' in vals:
        j = vals.index('=') - 1
        while j >= 0 and vals[j] == ']':  # skip every [ ... ] group (sizes may be enum names)
            d = 0
            while j >= 0:
                if vals[j] == ']':
                    d += 1
                elif vals[j] == '[':
                    d -= 1
                    if d == 0:
                        break
                j -= 1
            j -= 1
        while j >= 0 and head[j][0] != 'id':
            j -= 1
        return (vals[j], 'table') if j >= 0 else None
    for kw in ('struct', 'enum', 'union', 'class'):
        if kw in vals:
            ids = [t[1] for t in head if t[0] == 'id' and t[1] not in KEYWORDS]
            return ((ids[-1] if ids else '<anon>'), kw)
    if ')' in vals:
        # function: identifier right before the '(' that matches the last ')'
        close = len(vals) - 1 - vals[::-1].index(')')
        d, j = 0, close
        while j >= 0:
            if vals[j] == ')':
                d += 1
            elif vals[j] == '(':
                d -= 1
                if d == 0:
                    break
            j -= 1
        if j > 0 and head[j - 1][0] == 'id' and vals[j - 1] not in CONTROL:
            return vals[j - 1], 'function'
    return None


def norm(body, feature_ids=None):
    out = []
    for k, v, _ in body:
        if k == 'id' and v not in KEYWORDS:
            if feature_ids is None:
                out.append('$I')
            else:
                out.append('$F' if v in feature_ids else v)
        else:
            out.append(v)
    return out


def shingles(seq, k=4):
    if len(seq) < k:
        return {tuple(seq)} if seq else set()
    return {tuple(seq[i:i + k]) for i in range(len(seq) - k + 1)}


def literals(body):
    return {v for k, v, _ in body if k in ('num', 'str', 'chr')}


def callees(body):
    s = set()
    for i in range(len(body) - 1):
        k, v, _ = body[i]
        if k == 'id' and body[i + 1][1] == '(' and v not in CONTROL and v not in KEYWORDS:
            s.add(v)
    return s


def signature(b):
    if b['kind'] != 'function':
        return None
    vals = [t[1] for t in b['head']]
    try:
        p = vals.index('(')
    except ValueError:
        return None
    params = vals[p + 1:len(vals) - 1 - vals[::-1].index(')')]
    if params in ([], ['void']):
        nparam = 0
    else:
        d, nparam = 0, 1
        for v in params:
            if v in '([':
                d += 1
            elif v in ')]':
                d -= 1
            elif v == ',' and d == 0:
                nparam += 1
    ret = tuple(v for v in vals[:p - 1] if v in KEYWORDS or v == '*')
    return nparam, ret


def sig_cmp(a, b):
    if a is None or b is None:
        return '-'
    if a == b:
        return '='
    return '~' if a[0] == b[0] else '!'


def ratio(a, b):
    return len(a & b) / len(a) if a else 0.0


def iter_files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if os.path.splitext(f)[1].lower() in CODE_EXT:
                yield os.path.join(dp, f)


def load_blocks(path):
    return blocks(tokenize(blank_preprocessor(read_text(path))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ref-file', required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--ref-name')
    g.add_argument('--ref-lines', help='start-end; the block overlapping start is used')
    ap.add_argument('--root', required=True)
    ap.add_argument('--feature-ids', help='file with one identifier per line (request/feature-defined names)')
    ap.add_argument('--top', type=int, default=5)
    ap.add_argument('--min-tokens', type=int, default=15)
    ap.add_argument('--k', type=int, default=4, help='shingle size')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    ref_blocks = load_blocks(a.ref_file)
    ref = None
    if a.ref_name:
        cands = [b for b in ref_blocks if b['name'] == a.ref_name]
        ref = cands[0] if cands else None
    else:
        s, e = (int(x) for x in a.ref_lines.split('-'))
        for b in ref_blocks:
            if b['start'] <= e and b['end'] >= s:
                ref = b
                break
    if ref is None:
        sys.exit('reference block not found in %s' % a.ref_file)

    fids = None
    if a.feature_ids:
        with open(a.feature_ids, encoding='utf-8', errors='replace') as f:
            fids = {l.strip() for l in f if l.strip() and not l.startswith('#')}

    rb = ref['body']
    r_blind = shingles(norm(rb), a.k)
    r_named = shingles(norm(rb, fids), a.k) if fids is not None else None
    r_lits, r_calls, r_sig = literals(rb), callees(rb) - {ref['name']}, signature(ref)
    too_short = len(rb) < a.min_tokens

    rows = []
    for path in iter_files(a.root):
        try:
            bl = load_blocks(path)
        except Exception as ex:  # unreadable file: report, never stop
            print('WARN cannot parse %s: %s' % (path, ex), file=sys.stderr)
            continue
        for b in bl:
            cb = b['body']
            c_blind = shingles(norm(cb), a.k)
            row = {
                'file': os.path.relpath(path, a.root), 'name': b['name'], 'kind': b['kind'],
                'start': b['start'], 'end': b['end'],
                'blind': round(ratio(r_blind, c_blind), 3),
                'named': round(ratio(r_named, shingles(norm(cb, fids), a.k)), 3) if r_named is not None else None,
                'size': round(len(cb) / max(1, len(rb)), 2),
                'lits': '%d/%d' % (len(r_lits & literals(cb)), len(r_lits)),
                'calls': '%d/%d' % (len(r_calls & callees(cb)), len(r_calls)),
                'sig': sig_cmp(r_sig, signature(b)),
                '_set': c_blind,
            }
            rows.append(row)
    rows.sort(key=lambda r: (-r['blind'], -(r['named'] or 0), r['file'], r['start']))
    top = rows[:a.top]

    split = None
    if top and top[0]['blind'] < 0.6 and len(rows) >= 2:
        pool = rows[:10]
        best = None
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                cov = ratio(r_blind, pool[i]['_set'] | pool[j]['_set'])
                if best is None or cov > best[0]:
                    best = (cov, pool[i], pool[j])
        if best and best[0] >= 0.6:
            split = {'coverage': round(best[0], 3),
                     'parts': ['%s:%d-%d %s' % (p['file'], p['start'], p['end'], p['name']) for p in best[1:]]}

    for r in rows:
        r.pop('_set', None)
    result = {'reference': '%s:%d-%d %s (%s)' % (a.ref_file, ref['start'], ref['end'], ref['name'], ref['kind']),
              'ref_tokens': len(rb), 'too_short': too_short, 'top': top, 'possible_split': split}
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return
    print('reference: %s  tokens=%d%s' % (result['reference'], len(rb), '  TOO-SHORT (scores unreliable)' if too_short else ''))
    print('rank  blind  named  size   lits   calls  sig  candidate')
    for i, r in enumerate(top, 1):
        print('%-5d %-6.2f %-6s %-6s %-6s %-6s %-4s SRC:%s:%d-%d %s (%s)' % (
            i, r['blind'], '-' if r['named'] is None else '%.2f' % r['named'], '%.1fx' % r['size'],
            r['lits'], r['calls'], r['sig'], r['file'], r['start'], r['end'], r['name'], r['kind']))
    if split:
        print('possible SPLIT: coverage %.2f by %s' % (split['coverage'], ' + '.join(split['parts'])))


if __name__ == '__main__':
    main()
