import sys
# usage: setsec.py REPORT LETTER BODYFILE STATUS APPROVAL NEXT
p,L,bf,st,ap,nx=sys.argv[1:7]
s=open(p).read(); body=open(bf).read().rstrip()+'\n\n'
start=s.index(f'## Checkpoint {L} - ')
nxt=s.find('\n## Checkpoint ',start+5)
nxt=len(s) if nxt<0 else nxt+1
title=s[start:].split('\n',1)[0]
s=s[:start]+title+'\n'+body+s[nxt:]
import re
s=re.sub(rf'^\| {L} \|.*$',f'| {L} | {st} | {ap} | {nx} |',s,flags=re.M)
open(p,'w').write(s.rstrip()+'\n')
