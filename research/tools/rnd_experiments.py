"""Cycle experiments on the genuine Applesoft RND code (Apple ][+ ROM) via rnd_emu.py.
python rnd_experiments.py <rom> <experiment> [args]
  cold XX        : cold-start seed 80 4F C7 52 XX, iterate RND(1), find preperiod/period
  nofadd XX N    : compare N steps with and without the FADD at $EFC9 (patched to NOPs)
  neg n1,n2,...  : X=RND(-n) then iterate RND(1); report preperiod/period per n
Environment: CAP = max RND(1) calls before giving up (default 150000).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rnd_emu as E

CAP = int(os.environ.get('CAP', '150000'))


def run_cycle(mpu, mem):
    seen = {E.seed(mem): 0}
    outs = []
    for i in range(1, CAP + 1):
        E.call_rnd(mpu, mem, 1)
        s = E.seed(mem)
        if len(outs) < 12:
            outs.append(round(E.fac_value(mem), 9))
        if s in seen:
            return {'preperiod': seen[s], 'period': i - seen[s],
                    'first_repeat_call': i, 'first_outputs': outs}
        seen[s] = i
    return {'preperiod': None, 'period': None,
            'note': 'no cycle within %d calls' % CAP, 'first_outputs': outs}


exp = sys.argv[2]
if exp == 'cold':
    xx = int(sys.argv[3], 16)
    mpu, mem = E.make_mpu()
    mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, xx])
    r = run_cycle(mpu, mem)
    r['exp'] = 'cold $CD=%02X' % xx
    print(json.dumps(r))
elif exp == 'nofadd':
    xx = int(sys.argv[3], 16)
    N = int(sys.argv[4])
    a_mpu, a = E.make_mpu()
    b_mpu, b = E.make_mpu()
    for m in (a, b):
        m[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, xx])
    b[0xEFC9:0xEFCC] = bytes([0xEA, 0xEA, 0xEA])  # NOP out JSR FADD
    diff = None
    for i in range(1, N + 1):
        E.call_rnd(a_mpu, a, 1)
        E.call_rnd(b_mpu, b, 1)
        if E.seed(a) != E.seed(b):
            diff = i
            break
    print(json.dumps({'exp': 'nofadd $CD=%02X' % xx, 'steps': N, 'first_divergence': diff}))
elif exp == 'mkcycles':
    # mkcycles out.pkl : record the state sets of the known attractor cycles
    import pickle
    starts = [('cold', 0x00), ('cold', 0x58), ('neg', 25284), ('neg', 14189)]
    cycles = []
    for kind, v in starts:
        mpu, mem = E.make_mpu()
        mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, v if kind == 'cold' else 0])
        if kind == 'neg':
            E.call_rnd(mpu, mem, -v)
        seen = {E.seed(mem): 0}
        order = [E.seed(mem)]
        i = 0
        while True:
            i += 1
            E.call_rnd(mpu, mem, 1)
            s = E.seed(mem)
            if s in seen:
                cyc = order[seen[s]:]
                break
            seen[s] = i
            order.append(s)
        cycles.append(set(cyc))
        print('cycle from %s %d: length %d' % (kind, v, len(cyc)), flush=True)
    pickle.dump(cycles, open(sys.argv[3], 'wb'))
elif exp == 'classify':
    # classify cycles.pkl cold|neg v1,v2,... : steps until entering a known cycle
    import pickle
    cycles = pickle.load(open(sys.argv[3], 'rb'))
    kind = sys.argv[4]
    for v in [int(x, 0) for x in sys.argv[5].split(',')]:
        mpu, mem = E.make_mpu()
        mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, v if kind == 'cold' else 0])
        if kind == 'neg':
            E.call_rnd(mpu, mem, -v)
        seen = {E.seed(mem): 0}
        res = None
        for i in range(0, CAP + 1):
            s = E.seed(mem)
            hit = [len(c) for c in cycles if s in c]
            if hit:
                res = {'entered_cycle_len': hit[0], 'steps_to_enter': i}
                break
            if i:
                if s in seen:
                    res = {'new_cycle_len': i - seen[s], 'preperiod': seen[s]}
                    break
                seen[s] = i
            E.call_rnd(mpu, mem, 1)
        if res is None:
            res = {'note': 'unresolved within %d calls' % CAP}
        res['start'] = '%s %d' % (kind, v)
        print(json.dumps(res), flush=True)
elif exp == 'neg':
    for n in [int(x) for x in sys.argv[3].split(',')]:
        mpu, mem = E.make_mpu()
        mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, 0x00])
        E.call_rnd(mpu, mem, -n)
        r = run_cycle(mpu, mem)
        r['exp'] = 'RND(-%d)' % n
        r.pop('first_outputs')
        print(json.dumps(r), flush=True)
