import sys,re,shutil,os
OUT,SRC=sys.argv[1],sys.argv[2]; A=OUT+'/After'; W=OUT+'/_work'
d=open(W+'/D_plan.md').read()
log=[]
for m in re.finditer(r'### (P\d+) – (\S+) – (\S+) \((M\d+)\)\n(.*?)(?=\n### |\n## )',d,re.S):
    P,f,act,M,body=m.groups()
    path=A+'/'+f
    if act=='add-file':
        os.makedirs(os.path.dirname(path),exist_ok=True)
        shutil.copy2(SRC+'/'+f,path)
        n=sum(1 for _ in open(path)); log.append((P,M,f,f'1-{n}','applied','verbatim cp -p from SRC')); continue
    anchors=re.findall(r'TGT:\S+:(\d+) `([^`]*)`',body)
    blocks=re.findall(r'```\n(.*?)\n```',body,re.S)
    lines=open(path).read().split('\n')
    mode='replace' if '(replace' in body else 'after'
    res=[]
    # apply from bottom to top so line numbers stay valid
    pairs=list(zip(anchors,blocks))
    status='applied'; outlines=[]
    for (ln,txt),blk in sorted(pairs,key=lambda x:-int(x[0][0])):
        idx=[i for i,l in enumerate(lines) if l==txt]
        if len(idx)!=1: status='skipped (anchor not found)'; break
        i=idx[0]; new=blk.split('\n')
        if mode=='replace': lines[i:i+1]=new; outlines.append((i+1,i+len(new)))
        else: lines[i+1:i+1]=new; outlines.append((i+2,i+1+len(new)))
    open(path,'w').write('\n'.join(lines))
    log.append((P,M,f,','.join(f'{a}-{b}' if a!=b else f'{a}' for a,b in sorted(outlines)),status,mode))
for r in log: print('|'.join(r))
