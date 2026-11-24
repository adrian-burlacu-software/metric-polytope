# Level-7 lift columns over w1 / w2 (in the core's frame), marking which orbits have m_8-vertex children.
import json, sys
sys.path.insert(0,'.')
exec(open('phase9/round_13/maker/tower.py').read().split("if __name__")[0])
R=json.load(open('phase9/round_13/maker/tower.json'))
for name,k in W.items():
    useful={r['key']:len(r['outs']) for r in R[name]}
    w=P(k); seen={}
    print(name, 'core x8 matrix rows:')
    for i in range(6): print('   ',[0 if i==j else w.nums[pidx(6,min(i,j),max(i,j))] for j in range(6)])
    for z in lift(w):
        if z.D!=8: continue
        c=group.canonical(z).key()
        col=tuple(z.nums[pidx(7,j,6)] for j in range(6))
        seen.setdefault(c,[]).append(col)
    for c,cols in sorted(seen.items(), key=lambda kv:-useful.get(kv[0],0)):
        print(' outs',useful.get(c,0),'cols',cols[:4])
