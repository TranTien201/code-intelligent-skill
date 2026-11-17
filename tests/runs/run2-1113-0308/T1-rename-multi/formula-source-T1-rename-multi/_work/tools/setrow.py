import sys
rep,cp,status,appr,nxt=sys.argv[1:6]
L=open(rep).read().split('\n')
for k,l in enumerate(L):
    if l.startswith('| %s | '%cp) and l.count('|')==5:
        L[k]='| %s | %s | %s | %s |'%(cp,status,appr,nxt); break
open(rep,'w').write('\n'.join(L))
