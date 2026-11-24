src=open('sim4.py').read()
src=src.replace("json.dump(sorted(gain), open(f'phase9/round_14/maker/gain_{TAG}.json', 'w'))","json.dump(sorted(gain), open(f'phase9/round_16/maker/C_work/gain_{TAG}.json', 'w'))")
src=src.replace("""    for S in range(1 << (m - 1)):""","""    Sp = specials(Y, m)
    for i in range(m):
        for j in range(m):
            for Q in (Sp['dp'][j], Sp['ad'][j]):
                for t in TDB: out.add(tuple((1 - t) * p + t * q for p, q in zip(Sp['tw'][i], Q)))
    for S in range(1 << (m - 1)):""")
src=src.replace("PDF = sorted(","TDB = [F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4)]\nPDF = sorted(")
src=src.replace("""        elif c == 'cen':""","""        elif c.startswith('tri:'):
            # tri:K1.K2.K3:PAT@w1/w2/w3@...  K = kinds joined by '+', PAT over {i,j} e.g. iij; weights in all permutations
            _, kk, rest = c.split(':'); pt, *ws = rest.split('@'); ks = kk.split('.')
            W = set()
            for w in ws:
                for pm in itertools.permutations([F(x) for x in w.split('/')]): W.add(pm)
            Sp = Sp or specials(Y, m)
            for i in range(m):
                for j in range(m):
                    if 'j' in pt and i == j: continue
                    idx = [i if ch == 'i' else j for ch in pt]
                    for k1 in ks[0].split('+'):
                      for k2 in ks[1].split('+'):
                        for k3 in ks[2].split('+'):
                          A, B, Cc = Sp[k1][idx[0]], Sp[k2][idx[1]], Sp[k3][idx[2]]
                          for a, b, d in W: out.add(tuple(a * x + b * y + d * z for x, y, z in zip(A, B, Cc)))
                    if 'j' not in pt: break
        elif c == 'cen':""")
assert src.count('TDB')>=2 and 'tri:' in src
open('simC.py','w').write(src)
