import sys, itertools
def mat(n, nums):
    M = [[0]*n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i+1, n): M[i][j] = M[j][i] = next(it)
    return M
key=sys.argv[1]; n,D,rest=key.split('|'); n=int(n); D=int(D); M=mat(n,[int(a) for a in rest.split(',')])
for S in range(1<<(n-1)):
    Ss={i+1 for i in range(n-1) if S>>i&1}
    N=[[(D-M[a][b]) if ((a in Ss)!=(b in Ss)) else M[a][b] for b in range(n)] for a in range(n)]
    E=[(i,j,N[i][j]) for i,j in itertools.combinations(range(n),2) if not any(q not in (i,j) and N[i][q]+N[q][j]==N[i][j] for q in range(n))]
    W=set(w for _,_,w in E)
    if W<={2,3,4}:
        print(sorted(Ss), 'W',sorted(W), {w:[(i,j) for i,j,ww in E if ww==w] for w in sorted(W)})
        for r in N: print('   ',r)
