import sys,re
# usage: setsec.py REPORT "## Checkpoint X - title" bodyfile  ; replaces the section body (until next '## ')
rep,head,bodyf=sys.argv[1:4]
t=open(rep).read(); body=open(bodyf).read().rstrip('\n')+'\n\n'
i=t.index(head+'\n'); j=t.find('\n## ',i+len(head)); j = len(t) if j<0 else j+1
t=t[:i]+head+'\n'+body+t[j:]
open(rep,'w').write(t.rstrip('\n')+'\n')
