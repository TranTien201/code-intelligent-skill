import json,sys,os,shutil
SRC,OUT,W=sys.argv[1:4]
plan=json.load(open(os.path.join(W,"D_plan.json")))
log=[]; last_insert={}
for p in plan:
    f=os.path.join(OUT,p["file"]); m=p["mode"]
    if m=="add-file":
        os.makedirs(os.path.dirname(f),exist_ok=True)
        srcfile=os.path.join(SRC,p["file"]); shutil.copy2(srcfile,f)   # cp -p of whole source file
        n=len(open(f).read().split('\n'))-1
        log.append((p["pid"],p["file"],"1-%d"%n,"applied","add-file cp -p from "+p["src"])); continue
    if m=="ext-in-file":
        L=open(f).read().split('\n'); want=p["text"]
        # verify ext lines are present at position 21-27 of the copied file (written by P007 copy)
        ok = L[20:27]==want
        log.append((p["pid"],p["file"],"21-27","applied" if ok else "skipped (ext lines not found)","ext lines contained in cp -p copy (P007)")); continue
    t=open(f,newline='').read(); L=t.split('\n')
    if m=="insert-after-P020":
        anchor=plan[[q["pid"] for q in plan].index("P020")]["text"][-1]
    else:
        anchor=p["anchor_text"]
    idx=[i for i,l in enumerate(L) if l==anchor]
    if len(idx)!=1:
        log.append((p["pid"],p["file"],"-","skipped (anchor not found exactly once: %d)"%len(idx),"")); continue
    i=idx[0]
    if m=="replace":
        L[i:i+1]=p["text"]; a,b=i+1,i+len(p["text"])
    elif m=="replace3":
        L[i:i+3]=p["text"]; a,b=i+1,i+3
    else:
        L[i+1:i+1]=p["text"]; a,b=i+2,i+1+len(p["text"])
    open(f,'w',newline='').write('\n'.join(L))
    log.append((p["pid"],p["file"],"%d-%d"%(a,b) if b>a else "%d"%a,"applied",m))
json.dump(log,open(os.path.join(W,"E_log.json"),"w"),indent=1)
for r in log: print(r)
