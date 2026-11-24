import pickle, collections, itertools, sys
sys.argv=['x']; exec(open('tri_c.py').read().split('st=collections.Counter()')[0])
byt=collections.defaultdict(lambda: collections.defaultdict(set)); segst=collections.Counter()
for key,(Y,b,tids) in pairs.items():
    m=len(b); S=specials(Y,m)
    for (k1,P),(k2,Q) in itertools.combinations(S,2):
        dif=[q-p for p,q in zip(P,Q)]; nz=[i for i,x in enumerate(dif) if x]
        if not nz: continue
        t=(b[nz[0]]-P[nz[0]])/dif[nz[0]]
        if 0<t<1 and all(P[i]+t*dif[i]==b[i] for i in range(m)):
            o=sorted([(k1,1-t),(k2,t)],key=lambda z:(z[0][0],z[1])); f=('-'.join(k[0] for k,_ in o),pat([k for k,_ in o]))
            segst[(f,'/'.join(str(w) for _,w in o))]+=1
            for t_ in tids: byt[t_][f].add('/'.join(str(w) for _,w in o))
    for (k1,P),(k2,Q),(k3,R) in itertools.combinations(S,3):
        s=solve2(b,P,Q,R)
        if s and s[0]>0 and s[1]>0 and s[0]+s[1]<1:
            ws=(s[0],s[1],1-s[0]-s[1]); o=sorted(zip((k1,k2,k3),ws),key=lambda z:(z[0][0],z[1]))
            f=('-'.join(k[0] for k,_ in o),pat([k for k,_ in o]))
            for t_ in tids: byt[t_][f].add('/'.join(str(w) for _,w in o))
print(segst.most_common(30))
for t,d in byt.items():
    print('T',t,C[t]['D'],C[t]['s'])
    for f,w in sorted(d.items()): print('   ',f,sorted(w))
