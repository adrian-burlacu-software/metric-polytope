"""Current frontier (after round 5): unreached nodes with a reached one-node deletion; split by node D and by
the D of targets containing them."""
import json, sys, pickle, collections, time
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
st = pickle.load(open('checkpoints/phase9/engine/engine.pkl', 'rb'))
targets, tkeys, rep = st['targets'], st['tkeys'], st['rep']
R = set(json.load(open('checkpoints/phase9/reached.json')))
U = json.load(open('results/phase9/unreached_nodes.json')); UK = set(U['keys']); TK = set(U['target_keys'])
print('st keys', list(st.keys())); print('U keys', list(U.keys()))
def bits(m): return [v for v in range(m.bit_length()) if m >> v & 1]
def subkey(k, lm):
    tid, mask = rep[k]; T = bits(mask)
    return tkeys[tid][sum(1 << T[i] for i in bits(lm))]
front = []
for k in UK:
    if k not in rep: continue
    n = int(k.split('|')[0])
    if n < 4: continue
    full = (1 << n) - 1
    vs = [v for v in range(n) if subkey(k, full & ~(1 << v)) in R]
    if vs: front.append((k, vs))
print('frontier', len(front), sorted(collections.Counter(int(k.split('|')[0]) for k, _ in front).items()))
print('frontier by D', sorted(collections.Counter(int(k.split('|')[1]) for k, _ in front).items()))
print('unreached nodes by D', sorted(collections.Counter(int(k.split('|')[1]) for k in UK).items()))
# minimal unreached: all one-node deletions reached
json.dump({'front': front}, open('phase9/round_06/maker/frontier6.json', 'w'))
