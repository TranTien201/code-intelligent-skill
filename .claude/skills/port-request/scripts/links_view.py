#!/usr/bin/env python3
"""Render the request link graph (_work/A_links.md) as a Mermaid diagram + edge table for PORT_REPORT.md.

Deterministic, standard library only. Mermaid renders in VS Code (Markdown Preview Mermaid Support), GitHub, GitLab.

Usage:
  python3 -I links_view.py --links _work/A_links.md                              # after A: colour = stability
  python3 -I links_view.py --links _work/A_links.md --anchor _work/B_anchor.md   # after B: colour = anchor result,
                                                                                  # label adds the latest name
  [--out _work/A_links.mmd] [--no-table]
Input rows are the Markdown tables of work-artifacts.md:
  nodes  | N-id | name | kind | stability | def at | H-ids / S-id | component |
  edges  | from (N-id) | type | to (N-id) | evidence |
  anchor | id (file/N/S/H) | request location | latest location | anchor result | latest state | method | evidence | confidence |
"""
import argparse
import re
import sys

NID = re.compile(r'^N\d{3,}$')
STAB_CLASS = {'stable': 'stable', 'medium': 'medium', 'volatile': 'volatile'}
CLASS_DEFS = """    classDef stable fill:#d8f0dc,stroke:#2e7d32,color:#000
    classDef medium fill:#fff4cc,stroke:#b8860b,color:#000
    classDef volatile fill:#ffe0cc,stroke:#c85a00,color:#000
    classDef external fill:#eeeeee,stroke:#888888,color:#000,stroke-dasharray:4 3
    classDef same fill:#d8f0dc,stroke:#2e7d32,color:#000
    classDef renamed fill:#d6e6ff,stroke:#1f5fbf,color:#000
    classDef splitmerge fill:#ead9ff,stroke:#6a3fb5,color:#000
    classDef lowconf fill:#ffe0cc,stroke:#c85a00,color:#000,stroke-width:3px
    classDef missing fill:#ffd6d6,stroke:#c62828,color:#000,stroke-width:3px
    classDef open fill:#ffffff,stroke:#888888,color:#000"""


def cells(line):
    line = line.strip()
    if not line.startswith('|'):
        return None
    parts = re.split(r'(?<!\\)\|', line.strip('|'))
    return [p.strip().replace('\\|', '|') for p in parts]


def strip_md(s):
    return s.replace('`', '').strip()


def parse_links(path):
    nodes, edges, order = {}, [], []
    for line in open(path, encoding='utf-8', errors='replace'):
        c = cells(line)
        if not c or set(''.join(c)) <= set('-: '):
            continue
        c0 = strip_md(c[0])
        if NID.match(c0) and len(c) >= 4 and not NID.match(strip_md(c[2])):
            nodes[c0] = {'name': strip_md(c[1]), 'kind': strip_md(c[2]), 'stab': strip_md(c[3]).lower(),
                         'comp': strip_md(c[6]) if len(c) > 6 else ''}
            order.append(c0)
        elif NID.match(c0) and len(c) >= 3 and NID.match(strip_md(c[2])):
            edges.append((c0, strip_md(c[1]), strip_md(c[2]), strip_md(c[3]) if len(c) > 3 else ''))
    return nodes, order, edges


def parse_anchor(path):
    res = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        c = cells(line)
        if not c or len(c) < 4:
            continue
        c0 = strip_md(c[0])
        if NID.match(c0):
            res[c0] = {'latest': strip_md(c[2]), 'result': strip_md(c[3]),
                       'method': strip_md(c[5]) if len(c) > 5 else '',
                       'conf': strip_md(c[-1])}
    return res


def anchor_class(a):
    if a is None:
        return 'open'
    r, conf = a['result'].upper(), a['conf']
    if 'NOT_FOUND' in r or 'REWRITTEN' in r or 'MACRO' in r or 'REMOVED' in r:
        return 'missing'
    if conf.startswith('Low'):
        return 'lowconf'
    if 'SPLIT' in r or 'MERGED' in r:
        return 'splitmerge'
    if 'RENAMED' in r or 'MOVED' in r:
        return 'renamed'
    return 'same'


def esc(s):
    return s.replace('"', '#quot;').replace('<', '#lt;').replace('>', '#gt;')


def latest_name(loc):
    # "SRC:src/eco/eco.c:41-77 EcoMode_GetLevel" -> "EcoMode_GetLevel"; else last token
    toks = loc.split()
    return toks[-1] if toks else ''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--links', required=True)
    ap.add_argument('--anchor')
    ap.add_argument('--out')
    ap.add_argument('--no-table', action='store_true')
    a = ap.parse_args()

    nodes, order, edges = parse_links(a.links)
    if not nodes:
        sys.exit('no node rows found in %s (expected | N001 | name | kind | stability | ...)' % a.links)
    anc = parse_anchor(a.anchor) if a.anchor else None

    for f, _, t, _ in edges:  # endpoints that were not declared as nodes
        for n in (f, t):
            if n not in nodes:
                nodes[n] = {'name': n, 'kind': 'external', 'stab': 'external', 'comp': ''}
                order.append(n)

    out = ['```mermaid', 'flowchart LR']
    comps = {}
    for n in order:
        comps.setdefault(nodes[n]['comp'] or '', []).append(n)
    for comp, ns in comps.items():
        ind = '    '
        if comp:
            out.append('    subgraph %s["%s"]' % (re.sub(r'\W', '_', comp), esc(comp)))
            ind = '        '
        for n in ns:
            d = nodes[n]
            label = '%s<br/>%s · %s' % (esc(d['name']), esc(d['kind']), esc(d['stab']))
            if anc is not None:
                x = anc.get(n)
                if x:
                    ln = latest_name(x['latest'])
                    if ln and ln != d['name']:
                        label += '<br/>→ %s' % esc(ln)
                    label += '<br/>%s %s %s' % (esc(x['result']), esc(x['method']), esc(x['conf']))
                else:
                    label += '<br/>(not anchored)'
                cls = 'external' if d['kind'] == 'external' else anchor_class(x)
            else:
                cls = 'external' if d['kind'] == 'external' else STAB_CLASS.get(d['stab'], 'open')
            out.append('%s%s["%s"]:::%s' % (ind, n, label, cls))
        if comp:
            out.append('    end')
    for f, typ, t, _ in edges:
        out.append('    %s -->|%s| %s' % (f, esc(typ), t))
    out.append(CLASS_DEFS)
    out.append('```')
    legend = ('Legend: green = name kept · blue = renamed/moved · purple = split/merged · orange = Low confidence · '
              'red = not found/rewritten/removed · white = not anchored · grey dashed = outside the request'
              if anc is not None else
              'Legend: green = stable · yellow = medium · orange = volatile (trace order in B) · grey dashed = outside the request')
    out.append('')
    out.append(legend)
    if not a.no_table:
        out += ['', '| from | type | to | evidence |', '|---|---|---|---|']
        for f, typ, t, ev in edges:
            out.append('| %s `%s` | %s | %s `%s` | %s |' % (f, nodes[f]['name'], typ, t, nodes[t]['name'], ev.replace('|', '\\|')))
    text = '\n'.join(out) + '\n'
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(text)
    sys.stdout.write(text)


if __name__ == '__main__':
    main()
