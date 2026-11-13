#!/usr/bin/env python3
"""Turn one source line into a rename-tolerant POSIX ERE for `grep -E` (recipe R16).

No embeddings, standard library only. Output works with both BSD (macOS) and GNU grep.

Usage:
  python3 -I fuzzy_line.py 'level = TonerSave_GetLevel(nv->toner_save);'
  python3 -I fuzzy_line.py --abstract-file _work/B_feature_ids.txt 'level = TonerSave_GetLevel(nv->toner_save);'
  echo '<line>' | python3 -I fuzzy_line.py -
Then:  grep -rnE -e "$(python3 -I fuzzy_line.py ...)" "$SOURCE_ROOT" --include='*.c' --include='*.h'

Identifier handling:
  --abstract-file given : only the listed identifiers become wildcards (recommended: request/feature-defined
                          names that may have been renamed); all other identifiers stay literal.
  not given             : every non-keyword identifier becomes a wildcard (more matches, weaker evidence).
Literals, keywords and operators always stay literal. Whitespace between tokens is flexible.
stderr prints `kept=<n literal tokens> wild=<n wildcards>`; kept < 3 -> `WEAK` (pattern too generic to use alone).
"""
import argparse
import re
import sys

KEYWORDS = set("""
auto break case char const continue default do double else enum extern float for goto if inline int long
register restrict return short signed sizeof static struct switch typedef union unsigned void volatile while
_Bool bool true false NULL nullptr class namespace template typename public private protected virtual new delete
this operator using try catch throw constexpr
int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t size_t BOOL BYTE WORD DWORD TRUE FALSE
""".split())

TOKEN_RE = re.compile(r"""
    (?P<ws>\s+)
  | (?P<com>//.*$|/\*.*?\*/)
  | (?P<str>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])+')
  | (?P<num>0[xX][0-9A-Fa-f]+[uUlL]*|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?[uUlLfF]*)
  | (?P<id>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<op>->|\+\+|--|<<=|>>=|<<|>>|<=|>=|==|!=|&&|\|\||\+=|-=|\*=|/=|%=|&=|\|=|\^=|::|[^\sA-Za-z0-9_])
""", re.X)

ERE_META = set('.[]()*+?{}|^$\\')
WILD = '[A-Za-z_][A-Za-z0-9_]*'
SP0 = '[[:space:]]*'
SP1 = '[[:space:]]+'


def esc(s):
    out = []
    for ch in s:
        if ch in ERE_META:
            out.append('[' + ch + ']' if ch not in '\\^]' else '\\' + ch)
        else:
            out.append(ch)
    return ''.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('line', help="the source line, or '-' to read it from stdin")
    ap.add_argument('--abstract-file')
    a = ap.parse_args()
    line = sys.stdin.readline() if a.line == '-' else a.line
    line = line.rstrip('\r\n')

    abstract = None
    if a.abstract_file:
        with open(a.abstract_file, encoding='utf-8', errors='replace') as f:
            abstract = {l.strip() for l in f if l.strip() and not l.startswith('#')}

    parts, prev_word, kept, wild = [], False, 0, 0
    for m in TOKEN_RE.finditer(line):
        k, v = m.lastgroup, m.group()
        if k in ('ws', 'com'):
            continue
        is_word = k in ('id', 'num')
        if parts:
            parts.append(SP1 if (prev_word and is_word) else SP0)
        if k == 'id' and v not in KEYWORDS and (abstract is None or v in abstract):
            parts.append(WILD)
            wild += 1
        else:
            parts.append(esc(v))
            if k != 'op' or len(v) > 1:
                kept += 1
        prev_word = is_word
    if not parts:
        sys.exit('empty line')
    print(''.join(parts))
    print('kept=%d wild=%d%s' % (kept, wild, '  WEAK' if kept < 3 else ''), file=sys.stderr)


if __name__ == '__main__':
    main()
