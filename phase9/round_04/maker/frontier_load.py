st = pickle.load(open('checkpoints/phase9/engine/engine.pkl', 'rb'))
targets, tkeys, rep = st['targets'], st['tkeys'], st['rep']
R = set(json.load(open('checkpoints/phase9/reached.json')))
U = json.load(open('results/phase9/unreached_nodes.json')); UK = set(U['keys']); TK = set(U['target_keys'])
def bits(m): return [v for v in range(m.bit_length()) if m >> v & 1]
def subkey(k, lm):
    tid, mask = rep[k]; T = bits(mask)
    return tkeys[tid][sum(1 << T[i] for i in bits(lm))]
def point(k):
    tid, mask = rep[k]; return d2.restrict(d2.matrix(targets[tid]), targets[tid].D, bits(mask))
front = json.load(open('phase9/round_04/maker/frontier.json'))['front']
