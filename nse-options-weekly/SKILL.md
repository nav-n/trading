---
name: nse-options-weekly
description: |
  Weekly index-options analysis for NSE (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY). Reads index
  spot, multi-timeframe candles and option-chain data via Zerodha MCP, then recommends a CE or PE
  (buy, or hard-ruled naked sell), strike, entry trigger, stop-loss, targets and exit time.
  Drafts orders only after explicit user confirmation.

  Use when the user asks: "NIFTY call or put today", "weekly options setup", "which strike to buy",
  "BANKNIFTY option trade", "analyse option chain", "when to exit my CE/PE", "should I sell options
  this week", "weekly expiry trade", or any request for index-derivative trade ideas.
---

# NSE Weekly Options Analysis

Turns index spot + candles + option-chain data into a CE/PE trade plan with timed entry and exit.
Output is probabilistic scenarios with explicit invalidation levels, never a guarantee.

## Prerequisites

- **Zerodha MCP** (required for live data): `get_ltp`, `get_ohlc`, `get_quotes`,
  `get_historical_data`, `search_instruments`, `get_margins`, `get_positions`, `place_order`.
  If not logged in, call `login` first.
- Reuses these skills: `multi-timeframe-analysis`, `technical-analysis`, `rsi-divergence`,
  `fibonacci-trading`, `risk-reward-ratio`, `trailing-stops`.
- Without live data, ask the user to paste spot, candles and the option chain.

## Step 0: Verify contract facts (never hardcode)

Exchange rules change (weekly expiries, expiry weekdays, lot sizes). Before every analysis:

1. `search_instruments` for the index options and list the **actual nearest expiries available**.
   If an index has no weekly expiry, say so and use its monthly contract (or skip it).
2. Read **lot size** and strike step from the instrument data.
3. Compute **days to expiry (DTE)** from the real expiry date. Account for holidays.

## Workflow

```
1. DATA      -> Spot (get_ltp/get_ohlc), prev-day OHLC, India VIX, option chain quotes
2. BIAS      -> Weekly/daily trend (higher timeframe sets direction)
3. SETUP     -> 1h/15m structure: levels, RSI, VWAP, gap, pivots
4. TRIGGER   -> 5m/15m confirmation candle
5. CHAIN     -> OI, change in OI, PCR, max pain, IV/premium behaviour
6. SIGNAL    -> CALL / PUT / NO TRADE (confluence score)
7. STRIKE    -> Strike + side (buy or sell) by DTE and IV
8. PLAN      -> Entry, SL, targets, trail, time stop
9. SIZE      -> Lots from 1% risk and available margin
10. CONFIRM  -> Draft order; place only after explicit user approval
```

### 1. Data
- Index spot via `get_ltp` (e.g. `NSE:NIFTY 50`, `NSE:NIFTY BANK`); verify tradingsymbols with `search_instruments`.
- `get_historical_data` for: weekly (~6m), daily (~3m), 60m (~10 days), 15m (~3 days), 5m (today).
- Pull `get_quotes` for ATM and +/- 5 strikes (CE and PE): LTP, OI, volume, bid/ask.
- India VIX level and direction (rising VIX favours option buyers on breakouts; falling VIX
  with high premium favours sellers).

### 2-4. Trend and timing (use `multi-timeframe-analysis`)
| Timeframe | Role | Looks at |
|-----------|------|----------|
| Weekly / Daily | Bias | Trend, key S/R, prior week high/low |
| 60m / 15m | Setup | Structure, VWAP, pivots, RSI, divergences |
| 5m | Trigger | Break + close beyond level, volume expansion |

Intraday session context (IST):
- 9:15-9:30: opening volatility, wide spreads. Avoid entering unless gap + clear trigger.
- 9:30-11:30: best directional window.
- 11:30-13:30: usually choppy; theta bleeds buyers. Prefer no trade.
- 13:30-15:00: second directional window, especially expiry day.
- After ~15:00: avoid new buys; close intraday positions by ~15:15.

### 5. Option-chain read
| Signal | Bullish read | Bearish read |
|--------|-------------|--------------|
| Highest PE OI | Support strike (floor) | - |
| Highest CE OI | - | Resistance strike (ceiling) |
| PE OI rising + price up | Writers defending, bullish | - |
| CE OI rising + price down | - | Writers capping, bearish |
| OI falling with price rising (CE) | Short covering, bullish | - |
| PCR (OI based) | Above ~1.2 supportive | Below ~0.8 weak |
| Max pain | Magnet toward expiry, mostly useful in last 1-2 days | |

Treat PCR bands as rough guides, not rules. Needs OI change **vs previous close**, not just totals.

### 6. Signal (confluence score, max 10)
| Factor | Pts |
|--------|-----|
| Weekly + daily aligned with trade side | 2 |
| 60m/15m structure confirms (break of level, above/below VWAP) | 2 |
| 5m trigger candle with volume | 1 |
| Option chain OI supports (writers defending/capping) | 2 |
| RSI/divergence/Fib confluence | 1 |
| VIX and IV environment suits the structure (buy vs sell) | 1 |
| Time window favourable | 1 |

- **8-10**: full-size plan. **6-7**: half size. **Below 6: NO TRADE** (say so plainly).
- Opposing weekly vs intraday bias caps the score at 5.

### 7. Strike and side selection

**Buying (default):**
| DTE | Strike | Why |
|-----|--------|-----|
| 4+ | ATM or 1 ITM | Delta ~0.5-0.6, survives time decay |
| 2-3 | ATM | Balance of gamma and cost |
| 0-1 (expiry) | ATM or 1 OTM, small size | Gamma-driven; fast moves, fast decay |
- Avoid far-OTM "lottery" strikes; they need an outsized move.
- Skip buying if bid-ask spread > ~3% of premium or volume is thin.

**Naked selling (hard rules, only when ALL hold):**
1. Score is for a range/mean-reverting view or a strong wall (large OI) at the strike.
2. Strike at least ~1.5-2 standard daily moves away (use ATR/VIX-implied move) and beyond the
   high-OI strike on that side.
3. Mandatory stop-loss defined **before** entry (e.g. premium 2x-2.5x of entry, or index closes
   beyond the wall). Never sell without one.
4. `get_margins` shows enough margin; show **margin blocked and max realistic loss in Rs.**
5. Not on event days (RBI, budget, major results, expiry-day morning gap risk) unless user insists.
6. Warn that loss is theoretically unlimited and gaps can jump past stops. Suggest converting to a
   spread (buy a far hedge) as the safer alternative.

**Hedged selling: iron condor (defined risk, experimental, paper-trade only until validated)**
Four legs: sell OTM call + sell OTM put, buy a further OTM call + put (100-pt wings) as the hedge.
Profit if the index expires between the short strikes. Max loss is capped (about wing width - credit).
- Backtest (NIFTY daily closes, Jan 2022 - Oct 2026, short strikes ~1.4-1.7% OTM, 0.167% credit):
  win rate 60-72% depending on entry day and hold; break-even is ~62%. Results swung from strongly
  positive to negative with entry timing, so **no proven edge**. Weeks with >1.7% moves happen ~35%
  of the time, and the worst weeks (-6.8%, +7.7%) hit max loss.
- Entry rules (ALL must hold):
  1. Net credit >= ~0.20% of spot (e.g. >= ~45 points at spot 22,500) after using real bid/ask,
     not last-traded prices. Below that, skip. (The backtest loses money at 0.10% and wins at 0.25%.)
  2. Short strikes at or beyond the high-OI walls (highest CE OI above, highest PE OI below) and at
     least ~1.5% from spot.
  3. Intraday/weekly bias is range-bound or the directional score is below 6 (no trend trade).
  4. Not within 1 trading day of RBI policy, budget, major results, or known gap events.
  5. `get_margins`/Zerodha basket margin shows the margin fits, and max loss <= the Rs. 1,500 cap
     is NOT achievable at 100-pt wings (~Rs. 4,000 max loss), so use narrower wings (e.g. 50 pts) or
     accept a larger cap explicitly in `PROTOCOL.md` before trading.
- Exit rules: close at 50% of max profit; close if the index touches a short strike; close all
  legs by the day before expiry. Never leg out of the hedge first. Close the losing short leg and
  its hedge together.
- Execution: place the long (hedge) legs first, then the short legs, so margin stays low and risk
  stays defined. Draft all four legs and confirm with the user before any order.
- Costs: 8 orders round trip, about Rs. 200-300 per condor; log them.

### 8. Trade plan template
```markdown
# [INDEX] [CE/PE] [BUY/SELL] | Expiry [date] | DTE [n]
**Signal:** CALL / PUT / NO TRADE  | Score x/10 | Bias: weekly [ ] daily [ ] intraday [ ]

**Index levels:** Entry trigger [spot] | Invalidation [spot] | T1 [spot] | T2 [spot]
**Option:** [SYMBOL] strike [x], LTP [p], lot size [n]
| Item | Premium | Index level | Note |
|------|---------|-------------|------|
| Entry | | | Trigger: 5m close above/below |
| Stop-loss | | | Hard SL, or index invalidation, whichever first |
| Breakeven | | | At +1R, move SL to cost |
| Target (2R) | | | Full lot exits here, or on trail |
**Time stop:** exit if no move by [HH:MM]; close all intraday by 15:15.
**R:R:** [x:1] (reject if below 1.5:1 for buys)
**Size:** [n] lots | Max loss Rs.[ ] (<=1% capital) | Margin/premium Rs.[ ]
**Scenarios:** Bull [%] / Bear [%] / Range [%]
```

### 9. Sizing (1% rule, use `position-sizing`)
```
risk_per_trade = 1% x capital   (capital from get_margins, or user-stated)
loss_per_lot   = (entry_premium - sl_premium) x lot_size   [buy]
lots           = floor(risk_per_trade / loss_per_lot)
```
Minimum 1 lot; if 1 lot exceeds the risk limit, report the trade as too large and say so.
Small-account mode (paper/early live, capital ~Rs. 25,000): 1 lot only, max loss Rs. 1,500 per trade
(see `paper-trading/PROTOCOL.md`); skip any setup whose required stop exceeds that cap.
Add costs: brokerage, STT on sell side premium, exchange charges, GST, slippage (use ~Rs.0.5-1
index points of premium as a slippage estimate on liquid strikes).

### Stop and target percentages (1R = the stop distance in premium points)
| Level | Premium move | Typical % of premium |
|-------|-------------|----------------------|
| Stop-loss | -1R | about -20% to -25% (Rs. 1,500 cap = 23 pts at lot 65) |
| Breakeven trigger | +1R | about +20% to +25% |
| Target | +2R | about +40% to +50% |
- Break-even win rate at 2:1 is ~36% before costs; the real edge must beat that.
- The target must also sit at a real index level (support/resistance/Fib). If the next level
  offers less than 1.5R, skip the trade. Percentages are a cross-check, not the primary rule.
- With 1 lot there are **no partial exits**: hold the full lot to 2R, move SL to cost at +1R, then
  trail or exit at target.

### Exit rules
- **Stop:** hit SL or invalidation level -> exit, no averaging down.
- **Targets:** exit at 2R; after +1R, trail with a 5m/15m structure or ATR trail
  (`trailing-stops`). Use partial booking only when holding 2+ lots.
- **Time:** theta-driven exit if premium flat after the time stop; close before 15:15 for intraday.
- **Positional (DTE 2+):** re-check bias each morning; exit if daily structure breaks. Do not
  carry long options into expiry-day close.
- **Sells:** buy back at 50-70% profit, or at the SL; never hold through expiry-day volatility.

## Execution safety
- Analysis is the default. **Never call `place_order` unless the user explicitly confirms** the
  exact symbol, side, quantity, order type and price in the current message.
- Draft order format: `SYMBOL | BUY/SELL | qty (lots x lot_size) | LIMIT price | product MIS/NRML`.
  Prefer LIMIT orders; place the SL as a separate order only after the entry fills and the user
  agrees.
- Approval for one order does not extend to the next.
- Check `get_positions` first to avoid doubling an existing position.

## Reality checks to state in every output
- Options buyers lose more often than they win; the edge is in selectivity (score >= 8) and
  cutting losses.
- Data may be delayed or incomplete; say when a field could not be fetched instead of guessing.
- Educational analysis, not financial advice. Derivatives trading can lose more than invested,
  especially when selling.
