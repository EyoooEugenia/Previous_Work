# QuantSys

A lightweight Python backtesting and charting tool for stocks and indices. Select tickers and strategies via config files, run `main.py`, and get candlestick charts plus backtest profit visualizations.

---

## Quick Start

```bash
python main.py
```

The script will:
1. Read `config/stock_config.json` to know which tickers to download and which strategy to apply to each.
2. Download price data via `yfinance`.
3. Run the chosen strategy for each ticker.
4. Render two figures per ticker:
   - A 4-panel chart: K-line + SMA, Volume, KDJ, MACD.
   - A 3-panel backtest report: cumulative cash, price retracement, strategy vs. benchmark log-profit.

---

## Configuration

### 1. `config/stock_config.json` — Choose tickers, strategies, and date range

This is the main file you will edit. Structure:

```json
{
  "Index": {
    "HangSengIndex": { "ticker": "^HSI",  "strategy": "donchian_ATR" },
    "S&P500":        { "ticker": "^GSPC", "strategy": "donchian" }
  },
  "Stock": {
    "Apple":     { "ticker": "AAPL", "strategy": "donchian" },
    "Microsoft": { "ticker": "MSFT", "strategy": "donchian" }
  },
  "Date": {
    "Start": "2025-01-01",
    "End":   "2025-12-31"
  }
}
```

| Field | Meaning |
|---|---|
| Top-level keys (`Index`, `Stock`, ...) | Purely organizational. Add any category name you like — the loader iterates every key except `Date`. |
| Inner name (`"Apple"`, `"HangSengIndex"`, ...) | Display label used in logs and chart titles. |
| `ticker` | Any ticker symbol accepted by [yfinance](https://pypi.org/project/yfinance/) (e.g. `"AAPL"`, `"^HSI"`, `"0700.HK"`). |
| `strategy` | Strategy key. Must match a key in the `STRATEGY_MAP` in `main.py` (see **Strategies** below). |
| `Date.Start` / `Date.End` | Backtest window, `YYYY-MM-DD`. Passed directly to `yfinance.download`. |

**To add a new stock**, just append a new entry under any category, e.g.:

```json
"Stock": {
  "Apple":  { "ticker": "AAPL", "strategy": "donchian" },
  "Tesla":  { "ticker": "TSLA", "strategy": "donchian_ATR" }
}
```

**To remove a stock**, delete its entry. **To change the backtest period**, edit `Date.Start` / `Date.End`.

---

### 2. `config/chart_config.json` — Technical chart layout

Controls the 4-panel price chart. You usually don't need to touch this, but you can:

- `layout_dict`: matplotlib `subplots_adjust` parameters (`figsize`, `hspace`, `height_ratios`, etc.).
- `subplots_dict`: which indicators to draw, in order `graph_fst` → `graph_fth`. Each subplot takes:
  - `graph_name`: renderer (`kgraph`, `volgraph`, `kdjgraph`, `macdgraph`).
  - `graph_type`: indicator parameters. For `kgraph`, `sma` is a list of moving-average windows (default `[20, 30, 60]`).

---

### 3. `config/trace_config.json` — Backtest report layout

Controls the 3-panel backtest output. The most useful knobs are inside `trace_subplots.trace_fst.graph_type.cash_profit`:

| Field | Default | Meaning |
|---|---|---|
| `cash_hold` | `100000` | Starting cash for the simulated portfolio. |
| `slippage` | `0.01` | Per-trade slippage. |
| `c_rate` | `0.0003` | Commission rate (0.03%). |
| `t_rate` | `0.001` | Transaction tax / stamp duty (0.1%). |

Adjust these to match your broker's fee structure.

---

## Strategies

The strategies live in `strategies.py` and are registered in `main.py` via:

```python
STRATEGY_MAP = {
    "donchian":     strategies.get_ndays_singal,
    "donchian_ATR": strategies.get_ndays_ATR_singal
}
```

Use the **key** (e.g. `"donchian_ATR"`) as the `strategy` value in `stock_config.json`.

### `donchian` — Donchian Channel Breakout

Classic trend-following breakout.

- **Buy signal**: today's close breaks above the highest high of the last **N1 = 15** days.
- **Sell signal**: today's close breaks below the lowest low of the last **N2 = 5** days.
- Position is held flat (-1) or long (+1) and forward-filled until the next signal.

### `donchian_ATR` — Donchian Breakout + ATR Stop

Same breakout entry as `donchian`, but adds ATR-based exit management using a 21-period ATR:

- **Stop-loss**: if price falls more than `n_loss × ATR21` below the entry price (default `n_loss = 1.8`), exit.
- **Take-profit**: if price rises more than `n_win × ATR21` above the entry price (default `n_win = 3.5`), exit.
- Exits are printed to the console with date and price.

Tune the parameters by editing the function signature in `strategies.py`:

```python
def get_ndays_ATR_singal(stock_dat, N1=15, N2=5, n_win=3.5, n_loss=1.8):
```

### Adding a new strategy

1. Write a function in `strategies.py` that takes a DataFrame with `Open/High/Low/Close/Volume` columns and returns it with a `Signal` column (`1` = long, `-1` = flat).
2. Register it in `STRATEGY_MAP` in `main.py`:

   ```python
   STRATEGY_MAP = {
       "donchian":     strategies.get_ndays_singal,
       "donchian_ATR": strategies.get_ndays_ATR_singal,
       "my_strategy":  strategies.my_strategy_func,
   }
   ```

3. Reference it from `stock_config.json` via `"strategy": "my_strategy"`.

---

## Dependencies

```bash
pip install yfinance pandas numpy matplotlib TA-Lib
```

> `TA-Lib` requires the underlying C library. On macOS: `brew install ta-lib` first.

---

## File Layout

```
QuantSys/
├── main.py                  # Entry point — orchestrates download, strategy, plotting
├── strategies.py            # Strategy implementations (signal generation)
├── graph.py                 # Standalone chart helpers
├── MplVisualIf.py           # Low-level matplotlib wrapper
├── MultiGraphIf.py          # Multi-panel price-chart composer
├── MultiTraceIf.py          # Multi-panel backtest-report composer
└── config/
    ├── stock_config.json    # Tickers, strategy assignment, date range  ← edit this
    ├── chart_config.json    # Price-chart layout & indicators
    └── trace_config.json    # Backtest report layout & simulation params
```
