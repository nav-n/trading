# Indian Stock Trading Skills for Claude Code

> 9 AI-powered trading analysis skills for NSE/BSE Indian equity markets. Technical analysis, position sizing, risk management, Fibonacci, RSI divergence, and more — all inside your terminal.

**Zero dependencies.** Works standalone — just install the skills and ask Claude to analyze any stock. Optionally connect [Groww MCP](https://mcp.groww.in) for live market data or [yfinance](https://pypi.org/project/yfinance/) for historical analysis.

## What Are These?

[Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code/skills) are prompt-based frameworks that teach Claude how to perform specialized tasks. These skills turn Claude into a trading analyst that can:

- Analyze any NSE/BSE stock with technical indicators
- Calculate position sizes based on your risk tolerance
- Set intelligent stop-losses and trailing stops
- Identify RSI divergences and Fibonacci levels
- Score trade setups using multi-timeframe confluence
- Filter trades by risk-reward ratio

## Skills Included

| # | Skill | What It Does |
|---|-------|-------------|
| 1 | **nse-trading-toolkit** | Master orchestrator — coordinates all frameworks for full stock analysis |
| 2 | **technical-analysis** | Chart reading, trend ID, S/R levels, volume analysis, indicator dashboard, probabilistic scenarios |
| 3 | **position-sizing** | Fixed fractional, ATR-based, Kelly criterion sizing with leverage adjustments |
| 4 | **stop-loss-strategies** | Structure, ATR, S/R, and MA-based stop placement with buffer rules |
| 5 | **trailing-stops** | ATR trail, structure trail, MA trail, chandelier exit, hybrid approach |
| 6 | **risk-reward-ratio** | R:R calculation, minimum R:R by win rate, trade filtering, expected value |
| 7 | **multi-timeframe-analysis** | 3-screen method (weekly/daily/hourly), confluence scoring system |
| 8 | **rsi-divergence** | Regular + hidden divergence detection, confirmation rules, entry strategies |
| 9 | **fibonacci-trading** | Retracement entry zones, extension targets, confluence zone identification |

## Installation

### Option 1: Using skills CLI (Recommended)

```bash
npx skills add Bhala-Srinivash/nse-trading-skills
```

### Option 2: Manual install

```bash
# Clone the repo
git clone https://github.com/Bhala-Srinivash/nse-trading-skills.git

# Symlink all skills to your project
mkdir -p .claude/skills
for skill in nse-trading-skills/*/; do
  name=$(basename "$skill")
  [ -f "$skill/SKILL.md" ] || continue
  ln -s "$(cd "$skill" && pwd)" ".claude/skills/$name"
done
```

### Option 3: Install individual skills only

Only want position sizing and stop-loss? Copy just those:

```bash
mkdir -p .claude/skills/position-sizing .claude/skills/stop-loss-strategies
cp nse-trading-skills/position-sizing/SKILL.md .claude/skills/position-sizing/
cp nse-trading-skills/stop-loss-strategies/SKILL.md .claude/skills/stop-loss-strategies/
```

## Usage Examples

Once installed, just talk naturally:

```
"Analyze RELIANCE"
"Should I buy TATAMOTORS at current levels?"
"Position size for HDFCBANK with Rs.5 lakh account"
"Where to set stop-loss on my INFY trade at Rs.1,850?"
"RSI divergence on BBTC daily chart?"
"Fib levels for NIFTY from 24,000 to 22,000"
"Is this trade worth it? Entry 1800, stop 1700, target 2100"
"Trail my stop on SBIN — bought at 750, currently 820"
"Weekly vs daily trend on ICICIBANK"
```

## Data Sources (All Optional)

These skills work without any external data — you provide prices, Claude applies the frameworks. Connecting data sources enables auto-analysis:

### Groww MCP (Live Market Data)

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "growwmcp": {
      "command": "npx",
      "args": ["mcp-remote@0.1.18", "https://mcp.groww.in/mcp", "52155"]
    }
  }
}
```

Provides: live quotes, bid/ask depth, technical indicators (RSI, MACD, Bollinger, ADX, ATR), historical candles, portfolio holdings, and order placement.

### yfinance (Historical Data)

```bash
pip install yfinance
```

Claude writes Python scripts using yfinance when historical analysis is needed. NSE stocks use `.NS` suffix (e.g., `RELIANCE.NS`), BSE use `.BO`.

### TradingView MCP (Crypto Only)

For crypto screening. See [tradingview-mcp](https://github.com/pab-s/tradingview-mcp).

## How It Works

```
You: "Analyze BBTC"

Claude (using skills):
 1. Searches Groww for BBTC symbol
 2. Pulls live quote + technical indicators
 3. Runs multi-timeframe analysis (weekly bias → daily setup)
 4. Builds indicator dashboard (RSI, MACD, Bollinger, ADX)
 5. Identifies Fibonacci levels from swing points
 6. Checks for RSI divergences
 7. Presents 2-3 probabilistic scenarios
 8. Calculates position size based on your risk tolerance
 9. Sets stop-loss and trailing stop plan
10. Outputs concrete action plan with R:R ratios
```

## Indian Market Focus

These skills are specifically adapted for Indian equity markets:

- **Currency**: All examples and calculations in INR (Rs.)
- **Exchanges**: NSE and BSE symbol conventions
- **Trading hours**: 9:15 AM - 3:30 PM IST awareness
- **Settlement**: T+1 settlement cycle
- **Circuit limits**: 5%, 10%, 20% band awareness
- **Costs**: STT, brokerage, GST factored (~0.1% for delivery)
- **Broker integration**: Native [Groww](https://groww.in) support via MCP

## Compatible AI Agents

Standard SKILL.md format — works with:

- **Claude Code** (primary)
- **Cursor**
- **GitHub Copilot**
- **Cline**
- Any agent supporting the [Skills standard](https://skills.sh)

## Contributing

Want to add Ichimoku Cloud, Elliott Wave, VWAP, or Options strategies? PRs welcome!

1. Fork the repo
2. Create your skill directory with `SKILL.md`
3. Include a Prerequisites section
4. Submit a PR

## Disclaimer

These skills are educational tools for trading analysis. They do not constitute financial advice. Always do your own research and consult a financial advisor before making investment decisions. Trading involves risk of loss.

## License

MIT
