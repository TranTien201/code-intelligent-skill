import re,sys,subprocess
W=sys.argv[1]; REQ=sys.argv[2]
rows=[l for l in open(W+'/A_hunks.md') if l.startswith('| H0')]
def esc(s): return s.replace('|','\\|')
man=[]; llc={}
for r in rows:
    c=[x.strip() for x in r.strip().strip('|').split('|')]
    H,f,hh,br,ar,pt,sym,fs,ml,pl,no=c
    path=f.strip('`')
    st='added' if 'toner_save/' in path else 'modified'
    if sym.startswith('N/A'):
        man.append(f"| {no} | {f} | {st} | N/A (non-code file) | unknown | N/A | N/A |"); continue
    a,b=(ar[1:].split('-L')+[None])[:2]; a=int(a); b=int(b) if b else a
    lines=open(f"{REQ}/After/{path}").read().split('\n')
    seg=[(n,lines[n-1]) for n in range(a,b+1)]
    cell=lambda n,t: f"L{n}: `{esc(t)}`" if t.strip() else f"L{n}: (blank)"
    if len(seg)<=3: after='<br>'.join(cell(n,t) for n,t in seg)
    else: after='<br>'.join(cell(n,t) for n,t in seg[:2])+f"<br>… (+{len(seg)-2} lines, {H})"
    man.append(f"| {no} | {f} | {st} | {sym} | {fs} | N/A | {after} |")
    llc.setdefault(path,[]).extend((H,cell(n,t)) for n,t in seg)
print('\n'.join(man)); print('@@LLC')
for p,v in llc.items():
    print(f"#### `{p}`\n| H-id | Modified_Before (-) | Modified_After (+) |\n|---|---|---|")
    for H,c in v: print(f"| {H} |  | {c} |")
    print()
