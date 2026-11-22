import sys, time, json, random
sys.path.insert(0, 'scripts/phase9'); sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
from common import interpreter
import pickle, detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
I, names = interpreter(['phase9/round_05/maker/01_partial_dup.mpr', 'phase9/round_05/maker/02_partial_pendant.mpr'])
random.seed(1)
Rl = [k for k in R if k in rep]
for name in ('partial-dup', 'partial-pendant'):
    for n in (6, 7, 8):
        ks = random.sample([k for k in Rl if int(k.split('|')[0]) == n], 3)
        tot = 0; I.apply_move(I.moves[name], [point(ks[0])], as_orbits=True); t0 = time.time()
        for k in ks:
            p = point(k); outs = I.apply_move(I.moves[name], [p], as_orbits=True); tot += len(outs)
        print(name, 'n', n, 'mode', I.move_mode(I.moves[name], [p]), 'outputs/input', tot // 3, 'sec/input', round((time.time() - t0) / 3, 2), flush=True)
