#!/usr/bin/env python3
"""Search ladder for port-changelog (OVERVIEW §5, CONTRACT §4 "locate.py"). Standard library only.

Rungs: 1 name (find_unit) -> 2 exact / normalized block match -> 3 rare-token anchors ->
4 fuzzy windows (difflib + rename-tolerant shingle similarity) -> 5 LLM (caller, via decide()).
Every score used for a threshold is computed here, never by an LLM.

CLI:
  locate.py unit  --name N --root R [--ref-file F --ref-name N] [--hint FILE ...]
  locate.py block --block-file B --file F [--from L1 --to L2]
"""
import argparse
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (C_KEYWORDS, IDENT_RE, best_unit, find_units, grep_files,  # noqa: E402
                    iter_code_files, mask_comments_strings, norm_line, read_src)

# Tokenizer (from port-request/similarity.py): comments dropped, literals kept whole.
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
SHINGLE = 4


def _fix_comment_edges(text):
    """A block cut out of a file may start inside or end inside a /* */ comment: close it."""
    o, c = text.find('/*'), text.find('*/')
    if c >= 0 and (o < 0 or c < o):
        text = '/*' + text
    if text.rfind('/*') > text.rfind('*/'):
        text += '*/'
    return text


def tokenize(lines, fix_edges=False):
    """[(kind, value, line_index_0based)] with comments and whitespace dropped."""
    text = '\n'.join(lines)
    if fix_edges:
        text = _fix_comment_edges(text)
    toks, ln = [], 0
    for m in TOKEN_RE.finditer(text):
        kind, val = m.lastgroup, m.group()
        if kind not in ('ws', 'lcom', 'bcom'):
            toks.append((kind, val, ln))
        ln += val.count('\n')
    return toks


def line_tokens(lines, fix_edges=False):
    """Per-line token values (comments/whitespace dropped)."""
    toks = [[] for _ in lines]
    for _, v, ln in tokenize(lines, fix_edges):
        if ln < len(toks):
            toks[ln].append(v)
    return toks


def line_keys(lines, fix_edges=False):
    """Per-line whitespace/comment-insensitive key ('' when the line has no code)."""
    return [' '.join(t) for t in line_tokens(lines, fix_edges)]


# ----------------------------------------------------------------------------------------------
# Similarity
# ----------------------------------------------------------------------------------------------
def _shingles(toks, blind):
    vals = ['$I' if (blind and k == 'id' and v not in C_KEYWORDS) else v for k, v, _ in toks]
    n = min(SHINGLE, len(vals))
    return {tuple(vals[i:i + n]) for i in range(len(vals) - n + 1)} if n else set()


def _containment(a, b):
    return len(a & b) / len(a) if a else 0.0


def similarity(a_lines, b_lines):
    """0..1 containment of a's 4-token shingles in b (a grown b is not penalised).
    0.5 * blind (identifiers -> $I, rename tolerant) + 0.5 * named (identifiers literal)."""
    ta, tb = tokenize(a_lines, True), tokenize(b_lines, True)
    if not ta:
        return 0.0
    n = min(SHINGLE, len(ta))
    blind = _containment(_shingles(ta, True), _shingles(tb, True)) if len(tb) >= n else 0.0
    named = _containment(_shingles(ta, False), _shingles(tb, False)) if len(tb) >= n else 0.0
    return round(0.5 * blind + 0.5 * named, 4)


# ----------------------------------------------------------------------------------------------
# Definition index
# ----------------------------------------------------------------------------------------------
def _enumerators(unit):
    masked = mask_comments_strings(unit.body)
    m = re.search(r'\benum\b[^{]*\{(.*)\}', masked, re.S)
    if not m:
        return set()
    out = set()
    for part in m.group(1).split(','):
        mm = IDENT_RE.match(part.strip())
        if mm:
            out.add(mm.group(0))
    return out


class DefIndex:
    """Lazy symbol-definition index over a tree (grep -rlw, then find_units on hit files)."""

    def __init__(self, root):
        self.root = root
        self._units = {}
        self._defs = {}

    def units(self, relpath):
        if relpath not in self._units:
            p = os.path.join(self.root, relpath)
            self._units[relpath] = find_units(read_src(p).text) if os.path.isfile(p) else []
        return self._units[relpath]

    def defs_in(self, name, files):
        out = []
        for rel in grep_files(self.root, name, files):
            for u in self.units(rel):
                if u.name == name or (u.kind == 'decl' and name in _enumerators(u)):
                    out.append((rel, u))
        return out

    def defs(self, name):
        if name not in self._defs:
            self._defs[name] = self.defs_in(name, None)
        return self._defs[name]

    def has(self, name):
        return bool(self.defs(name))


def _cand(path, u, score):
    return {"path": path, "name": u.name, "start": u.start, "end": u.end, "score": round(score, 4)}


def find_unit(name, kind, ref_lines, root, hint_files=None, index=None, hi=0.9, lo=0.6):
    """Rung 1 (by name: hint files first, then whole tree) then rename search by similarity."""
    index = index or DefIndex(root)
    ok_kind = (lambda u: kind is None or u.kind == kind or u.name != name)  # enum-const decls pass
    hits = [d for d in index.defs_in(name, list(hint_files)) if ok_kind(d[1])] if hint_files else []
    if not hits:
        hits = [d for d in index.defs(name) if ok_kind(d[1])]
    if hits:
        scored = [(similarity(ref_lines, u.lines) if ref_lines else 1.0, p, u) for p, u in hits]
        order = {'func': 0, 'macro': 1, 'decl': 2}
        scored.sort(key=lambda t: (-t[0], order.get(t[2].kind, 9), -(t[2].end - t[2].start)))
        s, p, u = scored[0]
        return {"status": "found", "path": p, "unit": u, "score": round(s, 4), "method": "name",
                "candidates": [_cand(pp, uu, ss) for ss, pp, uu in scored[:3]]}
    scored = []
    if ref_lines:
        files = list(hint_files) if hint_files else iter_code_files(root)
        min_len = max(1, int(0.3 * len([l for l in ref_lines if l.strip()])))
        for rel in files:
            for u in index.units(rel):
                if (kind is None or u.kind == kind) and len(u.lines) >= min_len:
                    scored.append((similarity(ref_lines, u.lines), rel, u))
        scored.sort(key=lambda t: -t[0])
    cands = [_cand(p, u, s) for s, p, u in scored[:3]]
    if not scored or scored[0][0] < lo:
        return {"status": "missing", "path": None, "unit": None,
                "score": round(scored[0][0], 4) if scored else 0.0, "method": "similarity",
                "candidates": cands}
    s, p, u = scored[0]
    return {"status": "renamed" if s >= hi else "llm", "path": p, "unit": u, "score": round(s, 4),
            "method": "similarity", "candidates": cands}


# ----------------------------------------------------------------------------------------------
# Block location (rungs 2-4)
# ----------------------------------------------------------------------------------------------
def _window_score(bkeys, block_lines, wkeys, wlines):
    # token-level ratio (a line-level ratio is too coarse for 1-3 line blocks)
    a, b = ' '.join(bkeys).split(' '), ' '.join(wkeys).split(' ')
    ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    return 0.5 * ratio + 0.5 * similarity(block_lines, wlines)


def locate_block(block_lines, lines, lo_line=1, hi_line=None):
    """Candidates [{"start","end","score","method"}] (1-based inclusive in `lines`), best first."""
    hi_line = min(hi_line or len(lines), len(lines))
    bkeys = [k for k in line_keys(block_lines, True) if k]
    if not bkeys or lo_line > hi_line:
        return []
    alltoks = line_tokens(lines)
    allkeys = [' '.join(t) for t in alltoks]
    rng = [(i + 1, allkeys[i]) for i in range(lo_line - 1, hi_line) if allkeys[i]]  # (lineno, key)
    keys = [k for _, k in rng]
    line_toks = [set(alltoks[ln - 1]) for ln, _ in rng]
    nb, nr = len(bkeys), len(rng)
    code_block = [l for l, k in zip(block_lines, line_keys(block_lines, True)) if k]

    # Rung 2: exact contiguous run of code lines.
    out = []
    for i in range(nr - nb + 1):
        if keys[i:i + nb] == bkeys:
            s, e = rng[i][0], rng[i + nb - 1][0]
            raw = [l for l in lines[s - 1:e] if l.strip()]
            exact = [l.rstrip() for l in raw] == [l.rstrip() for l in block_lines if l.strip()]
            out.append({"start": s, "end": e, "score": 1.0, "method": "exact" if exact else "normalized"})
    if out or not nr:
        return out

    def span(i, n):
        return rng[i][0], rng[min(i + n, nr) - 1][0]

    def score(i, n):
        s, e = span(i, n)
        wl = [l for l, k in zip(lines[s - 1:e], allkeys[s - 1:e]) if k]
        return _window_score(bkeys, code_block, keys[i:i + n], wl)

    lens = sorted({max(1, int(nb * 0.7)), nb, max(1, -(-nb * 13 // 10))} |
                  set(range(max(1, int(nb * 0.7)), -(-nb * 13 // 10) + 1)))
    found = {}

    def consider(i, method):
        for n in lens:
            j = max(0, min(i, nr - 1))
            n = min(n, nr - j)
            if (j, n) in found:
                continue
            found[(j, n)] = (score(j, n), method)

    # Rung 3: rare-token anchors (identifiers/literals of the block rare in the range).
    btoks = {v for k, v, _ in tokenize(code_block) if k in ('id', 'num', 'str', 'chr')
             and v not in C_KEYWORDS}
    freq = {t: sum(1 for lt in line_toks if t in lt) for t in btoks}
    anchors = sorted((t for t in btoks if 0 < freq[t] <= max(3, nr // 50)), key=lambda t: freq[t])[:6]
    btl = [set(t) for t in line_tokens(code_block, True)]
    bpos = {t: next((p for p, s in enumerate(btl) if t in s), 0) for t in anchors}
    for t in anchors:
        for i, lt in enumerate(line_toks):
            if t in lt:
                for d in (-1, 0, 1):
                    consider(i - bpos[t] + d, 'anchor')

    # Rung 4: fuzzy windows; token-overlap prefilter, then full scoring of the best starts.
    bset = set().union(*btl)
    coarse = []
    for i in range(nr):
        w = set().union(*line_toks[i:i + nb])
        coarse.append((len(bset & w) / len(bset), i))
    coarse.sort(key=lambda t: -t[0])
    for _, i in coarse[:15]:
        for d in (-1, 0, 1):
            consider(i + d, 'fuzzy')

    cands = []
    for (i, n), (sc, method) in found.items():
        s, e = span(i, n)
        cands.append({"start": s, "end": e, "score": round(sc, 4), "method": method})
    cands.sort(key=lambda c: (-c["score"], c["method"] != 'anchor', c["end"] - c["start"]))
    kept = []
    for c in cands:  # dedupe overlapping windows, keep best
        if all(c["end"] < k["start"] or c["start"] > k["end"] for k in kept):
            kept.append(c)
    return kept[:10]


def decide(cands, hi=0.9, lo=0.6):
    if not cands:
        return "ask"
    scores = sorted((c["score"] for c in cands), reverse=True)
    best = scores[0]
    if best < lo:
        # a rare-token anchor hit is real evidence even when the text was rewritten -> LLM judges it
        top = max(cands, key=lambda c: c["score"])
        return "llm" if top.get("method") == "anchor" and best >= 0.25 else "ask"
    if best >= hi and (len(scores) == 1 or best - scores[1] >= 0.1):
        return "auto"
    return "llm"


def line_in(line, lines):
    key = norm_line(line)
    return any(norm_line(l) == key for l in lines)


# ----------------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------------
def _unit_json(u):
    return None if u is None else {"kind": u.kind, "name": u.name, "start": u.start, "end": u.end,
                                   "doc_start": u.doc_start}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    pu = sub.add_parser('unit')
    pu.add_argument('--name', required=True)
    pu.add_argument('--root', required=True)
    pu.add_argument('--kind')
    pu.add_argument('--ref-file')
    pu.add_argument('--ref-name')
    pu.add_argument('--hint', nargs='*')
    pb = sub.add_parser('block')
    pb.add_argument('--block-file', required=True)
    pb.add_argument('--file', required=True)
    pb.add_argument('--from', dest='lo', type=int, default=1)
    pb.add_argument('--to', dest='hi', type=int)
    a = ap.parse_args(argv)
    if a.cmd == 'unit':
        ref = None
        if a.ref_file:
            u = best_unit(find_units(read_src(a.ref_file).text), a.ref_name or a.name, a.kind)
            if u is None:
                print(json.dumps({"error": "ref unit not found"}))
                return 1
            ref = u.lines
        r = find_unit(a.name, a.kind, ref, a.root, a.hint)
        r["unit"] = _unit_json(r["unit"])
    else:
        cands = locate_block(read_src(a.block_file).lines, read_src(a.file).lines, a.lo, a.hi)
        r = {"decision": decide(cands), "candidates": cands}
    print(json.dumps(r, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
