# Paper-Trading Protocol (Rs. 25,000 virtual account)

Purpose: measure whether `nse-options-weekly` has a real edge before any real money is used.
No orders are placed. Every signal is logged in `journal.csv` and filled at realistic prices.

## Account rules
- Starting capital: Rs. 25,000 (virtual).
- NIFTY lot size is 65 (verify with `search_instruments`). Cost of 1 lot = premium x 65.
- **1 lot only.** Max premium allowed = Rs. 190 (about Rs. 12,350 per lot, under 50% of the account).
- **Max loss per trade: Rs. 1,500 (6% of capital)**, set by the stop-loss on premium:
  stop distance in points = 1,500 / 65 = ~23 points of premium. If the setup needs a wider stop, skip the trade.
  This is a known compromise: the skill's 1% rule (Rs. 250) cannot size one lot at this account size.
- **Stop / target (1R = stop distance, about 23 points):** stop at -1R (about -20% to -25% of premium),
  move stop to cost at +1R, target +2R (about +40% to +50% of premium, about Rs. 3,000 per lot).
  Skip any trade whose next real index level offers less than 1.5R. No partial exits with 1 lot:
  hold the full lot to 2R or the trailing stop.
- Only buy CE/PE. No selling: naked selling needs far more margin than this account.
- Max 1 open trade at a time. Max 2 trades per day. Stop for the day after 2 losses.
- Daily loss limit Rs. 2,500. Weekly loss limit Rs. 4,000: stop trading for the week if hit.

## Realistic fills (avoid flattering results)
- Entry at the **ask** at trigger time, exit at the **bid**.
- Costs per round trip: brokerage Rs. 40 + STT/charges/GST ~ Rs. 20-60 depending on premium. Log the estimate.
- Slippage: add 0.5-1 point per side.
- If the spread is above 3% of premium, skip and log "skipped: spread".

## Logging
One row per signal in `journal.csv`, including NO_TRADE signals (needed to test the filter).
Columns: date, time, index, signal (CALL/PUT/NO_TRADE), score, dte, symbol, entry, sl, t1, t2, exit, exit_reason, exit_time, gross_pnl, costs, net_pnl, notes.
Fill exit fields only from real subsequent data, never after-the-fact guesses.

## Iron condor track (separate paper account of Rs. 25,000 notional, not mixed with the directional journal)
- Log in `condor_journal.csv`, one row per condor, using real bid/ask for all four legs.
- Entry only if net credit >= ~0.20% of spot and the other entry rules in `SKILL.md` hold.
- Max loss per condor depends on wing width: 100-pt wings ~Rs. 4,000; use 50-pt wings (~Rs. 1,500-2,000)
  to stay near the per-trade cap, or record an explicit larger cap here before trading.
- One condor at a time; no directional trade while a condor is open.
- Pass lines same as the scorecard (100+ trades is a long time at 1 per week, so judge at 30+ trades for
  a first read, and treat it as inconclusive until 100).
- `condor_backtest.py` reproduces the historical test; run with `python -I condor_backtest.py <daily.json>`.

## Credibility scorecard
Compute after every 20 trades, judge only at 100+ trades (under 30 trades proves nothing).

| Metric | Pass line |
|--------|-----------|
| Trades logged | >= 100 over >= 8 weeks, mixed market conditions |
| Net expectancy per trade | > 0 after costs |
| Profit factor | > 1.3 |
| Win rate vs avg win/loss | consistent with R:R (e.g. 40% wins needs avg win > 1.5x avg loss) |
| Max drawdown | < 30% of Rs. 25,000 (Rs. 7,500) |
| Score >= 8 trades beat score 6-7 trades | confirms the scoring means something |
| NO_TRADE days | would-be trades on those days lose on average |

If expectancy is negative after 100 trades, change rules and restart the count; do not trade real money.

## Go-live gate (small real funds)
All pass lines met, 8+ weeks, no rule edits in the last 30 trades. Then start with 1 lot, a real account of
at least Rs. 25,000, and the same Rs. 1,500 per-trade cap.
