import json, sys
from collections import defaultdict

path = sys.argv[1]
rows = json.load(open(path, encoding="utf-8"))
d = [r["date"][:10] for r in rows]
o = [r["open"] for r in rows]
h = [r["high"] for r in rows]
l = [r["low"] for r in rows]
c = [r["close"] for r in rows]
n = len(c)
print("rows", n, d[0], d[-1])

LOT = 65
WING = 100 / 22520.0      # wing width as % of spot (current setup: 100 pts)
COST_RS = 250             # round trip, 4 legs open + 4 close, approx


def trade(i, H, call_d, put_d, k, managed=False):
    """Iron condor entered at close[i], held H trading days. Returns pnl in Rs and touched flag."""
    s = c[i]
    sc, lc = s * (1 + call_d), s * (1 + call_d + WING)
    sp, lp = s * (1 - put_d), s * (1 - put_d - WING)
    credit = k * s
    width = s * WING

    def val(x):
        # condor liability at underlying x (per unit)
        return (max(0, x - sc) - max(0, x - lc)) + (max(0, sp - x) - max(0, lp - x))

    j = i + H
    touched = max(h[i + 1:j + 1]) >= sc or min(l[i + 1:j + 1]) <= sp
    if managed:
        # exit at first daily close beyond a short strike at an assumed loss of 1x credit-less intrinsic + 50% of width
        for t in range(i + 1, j + 1):
            if c[t] >= sc or c[t] <= sp:
                loss = min(width, val(c[t]) + 0.25 * width)
                return (credit - loss) * LOT - COST_RS, touched
    pnl = (credit - val(c[j])) * LOT - COST_RS
    return pnl, touched


def run(H, call_d, put_d, k, step, managed=False, start=0):
    res, tch = [], 0
    i = start
    while i + H < n:
        p, t = trade(i, H, call_d, put_d, k, managed)
        res.append((d[i], p))
        tch += t
        i += step
    return res, tch


def stats(res):
    pn = [p for _, p in res]
    wins = sum(1 for p in pn if p > 0)
    eq, pk, dd = 0, 0, 0
    for p in pn:
        eq += p
        pk = max(pk, eq)
        dd = max(dd, pk - eq)
    return len(pn), wins / len(pn), sum(pn) / len(pn), min(pn), sum(pn), dd


print("\n=== Grid: hold 5 days, non-overlapping, held to expiry (no management) ===")
print("shortdist  credit%  trades  win%   avgRs   worstRs  totalRs  maxDD_Rs  touch%")
for dist in (0.010, 0.014, 0.017, 0.020, 0.025):
    for k in (0.0010, 0.00167, 0.0025):
        res, tch = run(5, dist, dist, k, 5)
        nT, w, avg, worst, tot, dd = stats(res)
        print(f"{dist*100:5.1f}%   {k*100:6.3f}  {nT:6d} {w*100:5.1f} {avg:8.0f} {worst:8.0f} {tot:9.0f} {dd:9.0f}  {tch/nT*100:5.1f}")

print("\n=== Current setup (call +1.69%, put -1.42%, credit 0.167%): by year, hold 5d ===")
byy = defaultdict(list)
res, tch = run(5, 0.0169, 0.0142, 0.00167, 5)
for dt, p in res:
    byy[dt[:4]].append(p)
for y in sorted(byy):
    v = byy[y]
    print(y, len(v), "win%", round(sum(1 for p in v if p > 0) / len(v) * 100, 1), "net Rs", round(sum(v)), "worst", round(min(v)))
print("ALL", stats(res), "touch%", round(tch / len(res) * 100, 1))

print("\n=== Same setup, hold 6d, offsets 0-4 averaged (robustness) ===")
tot = []
for off in range(5):
    res, tch = run(6, 0.0169, 0.0142, 0.00167, 6, start=off)
    s = stats(res)
    tot.append(s)
    print("offset", off, "trades", s[0], "win%", round(s[1] * 100, 1), "avgRs", round(s[2]), "totalRs", round(s[4]), "maxDD", round(s[5]))

print("\n=== Managed (exit on close beyond short strike at ~25% width loss + intrinsic), hold 5d ===")
res, tch = run(5, 0.0169, 0.0142, 0.00167, 5, managed=True)
print(stats(res))

print("\n=== Weekly range facts (5d close-to-close) ===")
rets = [(c[i + 5] / c[i] - 1) for i in range(n - 5)]
rets_s = sorted(rets)
print("mean %.2f%% std %.2f%%" % (sum(rets) / len(rets) * 100, (sum((x - sum(rets) / len(rets)) ** 2 for x in rets) / len(rets)) ** 0.5 * 100))
for thr in (0.010, 0.014, 0.017, 0.020, 0.025, 0.03):
    print("|ret|>%.1f%%: %.1f%% ; down<-%.1f%%: %.1f%% ; up>+%.1f%%: %.1f%%" % (
        thr * 100, sum(1 for x in rets if abs(x) > thr) / len(rets) * 100, thr * 100,
        sum(1 for x in rets if x < -thr) / len(rets) * 100, thr * 100, sum(1 for x in rets if x > thr) / len(rets) * 100))
print("worst 5d:", [round(x * 100, 2) for x in rets_s[:5]], "best 5d:", [round(x * 100, 2) for x in rets_s[-5:]])
