import json, glob, sys
from collections import Counter, defaultdict
pat = sys.argv[1]
by = defaultdict(Counter); bys = defaultdict(Counter)
for f in sorted(glob.glob(pat)):
    J = json.load(open(f))
    for ch in J['chains']:
        for s in ch['steps']:
            by[(ch['n'], s['dist'])][s['cls']] += 1
            bys[(ch['n'], s['step'])][s['cls']] += 1
for name, T in (('dist since last T', by), ('raw step', bys)):
    print(name)
    for k in sorted(T):
        c = T[k]; t = c['T'] + c['F'] + c['U']
        print(k, dict(c), f"F/tested={c['F']}/{t}")
