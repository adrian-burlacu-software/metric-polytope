# print the graphs (edges, v) of one-node covers for given D, piece types (see cross.py)
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'phase9/round_11/maker')
from cross import load, sw, piece
D=int(sys.argv[1]); la=F(int(sys.argv[2]),D); mu=F(int(sys.argv[3]),D)
dA=eval(sys.argv[4]); dB=eval(sys.argv[5]); src=sys.argv[6]; nA=len(dA); nB=len(dB)
for tid,X in load(8,D,src):
    n=len(X); seen=set()
    for v in range(n):
        rest=[i for i in range(n) if i!=v]
        for Ar in itertools.combinations(rest,nA-1):
            Br=[i for i in rest if i not in Ar]
            if len(Br)!=nB-1: continue
            A=list(Ar)+[v]; B=[v]+Br
            for m in range(1<<(n-1)):
                S={rest[i] for i in range(n-1) if m>>i&1}
                Y=sw(X,S); gA=piece(Y,A,la,dA)
                if not gA: continue
                gB=piece(Y,B,mu,dB)
                if not gB: continue
                EA=sorted((a,b) for a,b in itertools.combinations(sorted(A),2) if gA[(a,b)]==1)
                EB=sorted((a,b) for a,b in itertools.combinations(sorted(B),2) if gB[(a,b)]==1)
                k=(v,tuple(EA),tuple(EB))
                if k in seen: continue
                seen.add(k); print(tid,'v',v,'A',sorted(A),EA,'B',sorted(B),EB)
