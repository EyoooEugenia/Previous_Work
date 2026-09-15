import json
import yfinance as yf
from MultiGraphIf import MultiGraphIf
import graph
import matplotlib.pyplot as plt
from MultiTraceIf import MultiTraceIf
import numpy as np
import strategies
import pandas as pd

STRATEGY_MAP = {
    "donchian": strategies.get_ndays_singal,
    "donchian_ATR": strategies.get_ndays_ATR_singal
}


with open("config/stock_config.json", 'r') as load_f:
    stock_pool = json.load(load_f)

start_date = stock_pool['Date']['Start']
end_date = stock_pool['Date']['End']

stock_targets = []
tickers = []
for category, items in stock_pool.items():
    if category != "Date":
        for name, info in items.items():
            stock_targets.append((name, info['ticker'], info['strategy']))
            tickers.append(info['ticker'])

df_stockload = yf.download(tickers, start=start_date, end=end_date)

with open("config/chart_config.json", 'r') as cfg_f:
    chart_cfg = json.load(cfg_f)

with open("config/trace_config.json", 'r') as trace_f:
    trace_cfg = json.load(trace_f)

for stock_name, ticker, strategy_key in stock_targets:
    print(f"\n{stock_name} ({ticker}): {strategy_key}")

    try:
        if isinstance(df_stockload.columns, pd.MultiIndex):
            stock_dat = df_stockload.xs(ticker, level=1, axis=1).dropna().copy()
        else:
            stock_dat = df_stockload.dropna().copy()
    except KeyError:
        print(f"Data for {ticker} not found, skipping.")
        continue

    if stock_dat.empty:
        print(f"No valid data returned for {ticker}, skipping.")
        continue

    strategy_func = STRATEGY_MAP.get(strategy_key)
    if strategy_func:
        backtest_dat = strategy_func(stock_dat)
    else:
        print(f"Strategy for {strategy_key} not found, skipping.")
        continue


    draw_stock = MultiGraphIf(stock_dat, **chart_cfg['layout_dict'])
    draw_stock.graph_run(chart_cfg['subplots_dict'])

    draw_trace = MultiTraceIf(**trace_cfg['trace_layout'])
    draw_trace.graph_run(backtest_dat, **trace_cfg['trace_subplots'])