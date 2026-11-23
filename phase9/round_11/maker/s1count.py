# size/time of stage-1 and a sample of stage-2 fibers for a 2-stage proposal. args: file n s1expr s2expr
import sys, time
sys.path.insert(0,'scripts/phase9')
from common import interpreter
from metricpoly.dsl.interp import Env
from metricpoly.dsl.sexpr import read
from metricpoly.dsl.prims import _fiber_vertices
f,n=sys.argv[1],int(sys.argv[2])
I,names=interpreter([f])
t=time.time()
P=I.eval(read(sys.argv[3].replace('N',str(n))),Env())
Y=_fiber_vertices(P); t1=time.time()-t
print('stage1 holes',len(P.holes()),'verts',len(Y),'s',round(t1,1),flush=True)
t=time.time(); tot=0
for y in Y[:50]:
    Q=I.eval(read(sys.argv[4].replace('N',str(n))),Env(vars={'y':y}))
    tot+=len(_fiber_vertices(Q))
dt=time.time()-t
print('stage2 sample 50: verts',tot,'s',round(dt,2),'est total s',round(dt/50*len(Y),1))
