exec(open('phase9/round_03/maker/analyze2.py').read().split('C=collections')[0])
import sys
target=sys.argv[1]
cnt=0
for r in T8:
    x=mat(r); bs=best_switch(x)
    vals=[str(v) for v in bs[0][1]]
    if ','.join(vals)!=target: continue
    cnt+=1
    if cnt>4: continue
    nd,vals,S,y=bs[0]
    D=r['D']
    print('id',r['id'],'D',D,'S',S, 'num switchings achieving',len(bs))
    for v in vals:
        if v==max(vals): continue
        print('  ',v,[p for p,w in y.items() if w==v and p[0]<p[1]])
print(cnt)
