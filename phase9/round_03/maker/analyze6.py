exec(open('phase9/round_03/maker/analyze.py').read().split('stats=')[0])
st=collections.Counter(); byD=collections.defaultdict(collections.Counter)
apexT=[]
for r in T8:
    x=mat(r); n=8; ap=[]
    for i in range(n):
        vals=set(min(x[(i,j)],1-x[(i,j)]) for j in range(n) if j!=i)
        if len(vals)==1: ap.append((i,str(vals.pop())))
    st[len(ap)]+=1; byD[r['D']][len(ap)]+=1
    if ap: apexT.append((r['id'],r['D'],ap))
print(st); print(dict(byD)); print(apexT[:10])
