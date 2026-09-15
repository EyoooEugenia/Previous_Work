import numpy as np
from MplVisualIf import MplVisualIf

app = MplVisualIf()

def draw_kline_chart(stock_dat, stock_name="Stock"):
    layout_dict = {
        'figsize': (12, 6),
        'index': stock_dat.index,
        'draw_kind': {
            'ochl': {
                'Open': stock_dat['Open'],
                'Close': stock_dat['Close'],
                'High': stock_dat['High'],
                'Low': stock_dat['Low']
            }
        },
        'title': f"{stock_name} : K Line",
        'ylabel': "Price"
    }
    app.fig_output(**layout_dict)

def draw_volume_chart(stock_dat, stock_name="Stock"):
    bar_red = np.where(stock_dat['Open'] < stock_dat['Close'], stock_dat['Volume'], 0)
    bar_green = np.where(stock_dat['Open'] >= stock_dat['Close'], stock_dat['Volume'], 0)

    layout_dict = {
        'figsize': (14, 5),
        'index': stock_dat.index,
        'draw_kind': {
            'bar': {
                'bar_red': bar_red,
                'bar_green': bar_green
            }
        },
        'title': f"{stock_name} : Volume",
        'ylabel': "Volume",
        'legend': 'best'
    }
    app.fig_output(**layout_dict)

def draw_sma_chart(stock_dat, stock_name="Stock"):
    stock_dat['SMA20'] = stock_dat.Close.rolling(window = 20).mean()
    stock_dat['SMA30'] = stock_dat.Close.rolling(window = 30).mean()
    stock_dat['SMA60'] = stock_dat.Close.rolling(window = 60).mean()

    layout_dict = {
        'figsize': (14, 5),
        'index': stock_dat.index,
        'draw_kind': {
            'line': {
                'SMA20': stock_dat.SMA20,
                'SMA30': stock_dat.SMA30,
                'SMA60': stock_dat.SMA60
            }
        },
        'title': f"{stock_name} : Simple Moving Average",
        'ylabel': "Price",
        'legend': 'best'
    }
    app.fig_output(**layout_dict)

def draw_cross_annotate(stock_dat, stock_name="Stock"):
    stock_dat['Ma20'] = stock_dat.Close.rolling(window = 20).mean()
    stock_dat['Ma30'] = stock_dat.Close.rolling(window = 30).mean()

    list_diff = np.sign(stock_dat['Ma20'] - stock_dat['Ma30'])
    list_signal = np.sign(list_diff - list_diff.shift(1))
    down_cross = stock_dat[list_signal < 0]
    up_cross = stock_dat[list_signal > 0]

    layout_dict = {
        'figsize': (14, 5),
        'index': stock_dat.index,
        'draw_kind': {
            'line': {
                'SMA20': stock_dat.Ma20,
                'SMA30': stock_dat.Ma30
            },
            'annotate': {
                'down_cross': {
                    'andata': down_cross,
                    'va': 'top',
                    'xy_y': 'Ma20',
                    'xytext': (-20, 30),
                    'fontsize': 8,
                    'arrow': dict(facecolor = 'green', shrink = 0.1)
                },
                'up_cross': {
                    'andata': up_cross,
                    'va': 'bottom',
                    'xy_y': 'Ma20',
                    'xytext': (-20, -30),
                    'fontsize': 8,
                    'arrow': dict(facecolor = 'red', shrink = 0.1)
                }
            }
        },
        'title': f"{stock_name} : Moving Average Crossover",
        'ylabel': "Price",
        'legend': 'best'
    }
    app.fig_output(**layout_dict)

def draw_kdj_chart(stock_dat, stock_name="Stock"):
    low_list = stock_dat['Low'].rolling(9, min_periods = 1).min()
    high_list = stock_dat['High'].rolling(9, min_periods = 1).max()
    rsv = (stock_dat['Close'] - low_list) / (high_list - low_list) * 100
    stock_dat['K'] = rsv.ewm(com = 2, adjust = False).mean()
    stock_dat['D'] = stock_dat['K'].ewm(com = 2, adjust = False).mean()
    stock_dat['J'] = 3*stock_dat['K'] - 2 * stock_dat['D']

    layout_dict = {
        'figsize': (14, 5),
        'index': stock_dat.index,
        'draw_kind': {
            'line': {
                'K': stock_dat.K,
                'D': stock_dat.D,
                'J': stock_dat.J
            }
        },
        'title': f"{stock_name} : KDJ",
        'ylabel': "KDJ",
        'legend': 'best'
    }
    app.fig_output(**layout_dict)

def draw_macd_chart(stock_dat, stock_name="Stock"):
    macd_dif = stock_dat['Close'].ewm(span = 12, adjust = False).mean() - stock_dat['Close'].ewm(span = 26, adjust = False).mean()
    macd_dea = macd_dif.ewm(span = 9, adjust = False).mean()
    macd_bar = 2*(macd_dif - macd_dea)

    bar_red = np.where(macd_bar > 0, macd_bar, 0)
    bar_green = np.where(macd_bar < 0, macd_bar, 0)

    layout_dict = {
        'figsize': (14, 5),
        'index': stock_dat.index,
        'draw_kind': {
            'bar': {
                'bar_red': bar_red,
                'bar_green': bar_green
            },
            'line': {
                'macd dif': macd_dif,
                'macd dea': macd_dea
            }
        },
        'title': f"{stock_name} : MACD",
        'ylabel': "MACD",
        'legend': 'best'
    }
    app.fig_output(**layout_dict)

def draw_fibonacci_chart(stock_dat, stock_name="Stock"):
    Fib_max = stock_dat.Close.max()
    Fib_maxid = stock_dat.index.get_loc(stock_dat.Close.idxmax())
    Fib_min = stock_dat.Close.min()
    Fib_minid = stock_dat.index.get_loc(stock_dat.Close.idxmin())
    Fib_382 = (Fib_max - Fib_min) * 0.382 + Fib_min
    Fib_618 = (Fib_max - Fib_min) * 0.618 + Fib_min
    
    print(f"Fib0.382: {round(Fib_382, 2)}")
    print(f"Fib0.618: {round(Fib_618, 2)}")

    max_df = stock_dat[stock_dat.Close == stock_dat.Close.max()]
    min_df = stock_dat[stock_dat.Close == stock_dat.Close.min()]

    layout_dict = {
        'figsize': (14, 7),
        'index': stock_dat.index,
        'draw_kind': {
            'ochl': {
                'Open': stock_dat['Open'],
                'Close': stock_dat['Close'],
                'High': stock_dat['High'],
                'Low': stock_dat['Low']
            },
            'hline': {
                'Fib_382': {
                    'pos': Fib_382,
                    'c': 'r'
                },
                'Fib_618': {
                    'pos': Fib_618,
                    'c': 'r'
                }
            }, 
            'annotate': { 
                'max': {
                    'andata': max_df,
                    'va': 'bottom',
                    'xy_y': 'High',
                    'xytext': (-20, 30),
                    'fontsize': 8,
                    'arrow': dict(facecolor='red', shrink=0.1)
                },
                'min': {
                    'andata': min_df,
                    'va': 'top',
                    'xy_y': 'Low',
                    'xytext': (-20, -30),
                    'fontsize': 8,
                    'arrow': dict(facecolor='green', shrink=0.1)
                }
            }
        },
        'title': f"{stock_name} : Fibonacci Retracement",
        'ylabel': "Price",
        'legend': 'best'
    }
    app.fig_output(**layout_dict)