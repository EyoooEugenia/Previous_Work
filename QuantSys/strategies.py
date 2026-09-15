import numpy as np
from MplVisualIf import MplVisualIf
import talib

app = MplVisualIf()

# Donchian Channel Breakout Strategy
def get_ndays_singal(stock_dat, N1=15, N2=5):
    stock_dat['N1_High'] = stock_dat.High.rolling(window=N1).max()
    expan_max = stock_dat.High.expanding().max()
    stock_dat['N1_High'] = stock_dat['N1_High'].fillna(value=expan_max)

    stock_dat['N2_Low'] = stock_dat.Low.rolling(window=N2).min()
    expan_min = stock_dat.Low.expanding().min()
    stock_dat['N2_Low'] = stock_dat['N2_Low'].fillna(value=expan_min)

    buy_index = stock_dat[stock_dat.Close > stock_dat.N1_High.shift(1)].index
    sell_index = stock_dat[stock_dat.Close < stock_dat.N2_Low.shift(1)].index

    stock_dat.loc[buy_index, 'Signal'] = 1
    stock_dat.loc[sell_index, 'Signal'] = -1
    stock_dat['Signal'] = stock_dat['Signal'].shift(1)
    
    stock_dat['Signal'] = stock_dat['Signal'].ffill()
    stock_dat['Signal'] = stock_dat['Signal'].fillna(value=-1)

    return stock_dat

def draw_ndays_annotate(stock_dat, stock_name="Stock"):
    signal_shift = stock_dat.Signal.shift(1)
    signal_shift = signal_shift.fillna(value=-1)
    list_signal = np.sign(stock_dat.Signal - signal_shift)

    down_cross = stock_dat[list_signal < 0]
    up_cross = stock_dat[list_signal > 0]

    layout_dict = {
        'figsize': (14, 7),
        'index': stock_dat.index,
        'draw_kind': {
            'ochl': {
                'Open': stock_dat.Open,
                'Close': stock_dat.Close,
                'High': stock_dat.High,
                'Low': stock_dat.Low
            },
            'line': {
                'N1_High': stock_dat.N1_High,
                'N2_Low': stock_dat.N2_Low
            },
            'annotate': {
                'down': {
                    'andata': down_cross,
                    'va': 'top',
                    'xy_y': 'N2_Low',
                    'xytext': (-10, -30),
                    'fontsize': 8,
                    'arrow': dict(facecolor='green', shrink=0.1)
                },
                'up': {
                    'andata': up_cross,
                    'va': 'bottom',
                    'xy_y': 'N1_High',
                    'xytext': (-10, 30),
                    'fontsize': 8,
                    'arrow': dict(facecolor='red', shrink=0.1)
                }
            }
        },
        'title': f"{stock_name} : Donchian Channel Breakout",
        'ylabel': "Price",
        'xlabel': "Date",
        'xticks': 15,
        'legend': 'best',
        'xticklabels': '%Y-%m-%d'
    }
    app.fig_output(**layout_dict)

# Donchian Channel Breakout Strategy with ATR
def get_ndays_ATR_singal(stock_dat, N1=15, N2=5, n_win=3.5, n_loss=1.8):
    stock_dat['N1_High'] = stock_dat.High.rolling(window=N1).max()
    expan_max = stock_dat.High.expanding().max()
    stock_dat['N1_High'] = stock_dat['N1_High'].fillna(value=expan_max)

    stock_dat['N2_Low'] = stock_dat.Low.rolling(window=N2).min()
    expan_min = stock_dat.Low.expanding().min()
    stock_dat['N2_Low'] = stock_dat['N2_Low'].fillna(value=expan_min)

    stock_dat['ATR21'] = talib.ATR(stock_dat.High.values, stock_dat.Low.values, stock_dat.Close.values, timeperiod=21)

    buy_index = stock_dat[stock_dat.Close > stock_dat.N1_High.shift(1)].index
    sell_index = stock_dat[stock_dat.Close < stock_dat.N2_Low.shift(1)].index

    stock_dat.loc[buy_index, 'Signal'] = 1
    stock_dat.loc[sell_index, 'Signal'] = -1
    stock_dat['Signal'] = stock_dat['Signal'].shift(1)
    
    buy_price = 0
    
    for kl_index, today in stock_dat.iterrows():
        if (buy_price == 0) and (today.Signal == 1):
            buy_price = today.Close
        elif (buy_price != 0) and (buy_price > today.Close) and ((buy_price - today.Close) > n_loss * today.ATR21):
            print(f'Stop Loss Date: {kl_index.strftime("%Y-%m-%d")}, Stop Loss Price: {round(today.Close, 2)}')
            stock_dat.loc[kl_index, 'Signal'] = -1
            buy_price = 0
        elif (buy_price != 0) and (buy_price < today.Close) and ((today.Close - buy_price) > n_win * today.ATR21):
            print(f'Take Profit Date: {kl_index.strftime("%Y-%m-%d")}, Take Profit Price: {round(today.Close, 2)}')
            stock_dat.loc[kl_index, 'Signal'] = -1
            buy_price = 0
        elif (buy_price != 0) and (today.Signal == -1):
            stock_dat.loc[kl_index, 'Signal'] = -1
            buy_price = 0

    stock_dat['Signal'] = stock_dat['Signal'].ffill().fillna(-1)

    return stock_dat