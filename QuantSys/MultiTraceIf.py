import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys
from MplVisualIf import MplTypesDraw, DefTypesPool

class MultiTraceIf(MplTypesDraw):
    app = DefTypesPool()

    @app.route_types("cash_profit")
    def cash_profit_graph(stock_dat, sub_graph, para_dat):
        cash_hold = para_dat.get('cash_hold', 100000) if isinstance(para_dat, dict) else 100000
        slippage = para_dat.get('slippage', 0.01) if isinstance(para_dat, dict) else 0.01
        c_rate = para_dat.get('c_rate', 0.0003) if isinstance(para_dat, dict) else 0.0003
        t_rate = para_dat.get('t_rate', 0.001) if isinstance(para_dat, dict) else 0.001

        posit_num = 0
        skip_days = False
        buy_idx = 0
        buy_price = 0.0

        for idx_pos, (kl_index, today) in enumerate(stock_dat.iterrows()):
            if today.Signal == 1 and not skip_days:
                skip_days = True
                buy_idx = idx_pos
                buy_price = today.Close + slippage
                posit_num = int(cash_hold / buy_price)
                posit_num = int(posit_num / 100) * 100

                buy_cash = posit_num * buy_price
                commission = round(max(buy_cash * c_rate, 5), 2)
                cash_hold = cash_hold - buy_cash - commission
                
            elif today.Signal == -1 and skip_days:
                skip_days = False
                sell_idx = idx_pos
                sell_price = today.Close - slippage
                sell_cash = posit_num * sell_price

                commission = round(max(sell_cash * c_rate, 5), 2)
                tax = round(sell_cash * t_rate, 2)
                cash_hold = cash_hold + sell_cash - commission - tax

                fill_color = 'red' if sell_price >= buy_price else 'green'
                sub_graph.axvspan(buy_idx, sell_idx, color=fill_color, alpha=0.15)

            if skip_days:
                stock_dat.loc[kl_index, 'total'] = posit_num * today.Close + cash_hold
            else:
                stock_dat.loc[kl_index, 'total'] = cash_hold

        stock_dat['max_total'] = stock_dat['total'].expanding().max()
        stock_dat['per_total'] = stock_dat['total'] / stock_dat['max_total']

        type_dict = {
            'Portfolio Value': stock_dat.total,
            'Peak Portfolio Value': stock_dat.max_total
        }

        view_function = MplTypesDraw.mpl.route_output("line")
        view_function(stock_dat.index, type_dict, sub_graph)

        min_point_df = stock_dat.sort_values(by=['per_total'])[0:1] 
        drop_percent = round((1 - min_point_df.per_total.values[0]) * 100, 2)

        for idx_val, row in min_point_df.iterrows():
            idx_pos = stock_dat.index.get_loc(idx_val)
            sub_graph.annotate(
                f"Max Drawdown {drop_percent}%",
                xy=(idx_pos, row['total']),
                xytext=(0, -25),
                textcoords='offset points',
                ha='center', va='top',
                fontsize=8,
                arrowprops=dict(facecolor='green', shrink=0.1)
            )

    @app.route_types("cmp_profit")
    def cmp_profit_graph(stock_dat, sub_graph, para_dat):
        stock_dat['benchmark_profit_log'] = np.log(stock_dat.Close / stock_dat.Close.shift(1))
        
        signal_copy = stock_dat['Signal'].copy()
        signal_copy[signal_copy == -1] = 0
        stock_dat['trend_profit_log'] = signal_copy * stock_dat.benchmark_profit_log

        type_dict = {
            'Strategy Cum Return': stock_dat['trend_profit_log'].cumsum(),
            'Benchmark Cum Return': stock_dat['benchmark_profit_log'].cumsum()
        }

        view_function = MplTypesDraw.mpl.route_output("line")
        view_function(stock_dat.index, type_dict, sub_graph)

    @app.route_types("close_retrace")
    def close_retrace_graph(stock_dat, sub_graph, para_dat):
        stock_dat['max_close'] = stock_dat['Close'].expanding().max()
        stock_dat['per_close'] = stock_dat['Close'] / stock_dat['max_close']

        min_point_df = stock_dat.sort_values(by=['per_close'])[0:1]

        line_dict = {
            'Stock Close Price': stock_dat.Close,
            'Historical Max Price': stock_dat.max_close
        }
        view_function = MplTypesDraw.mpl.route_output("line")
        view_function(stock_dat.index, line_dict, sub_graph)

        retrace_percent = round((1 - min_point_df.per_close.values[0]) * 100, 2)
        
        for idx_val, row in min_point_df.iterrows():
            idx_pos = stock_dat.index.get_loc(idx_val)
            sub_graph.annotate(
                f"Stock Max Drawdown {retrace_percent}%",
                xy=(idx_pos, row['Close']),
                xytext=(0, -25),
                textcoords='offset points',
                ha='center', va='top',
                fontsize=8,
                arrowprops=dict(facecolor='green', shrink=0.1)
            )

    def __init__(self, **kwargs):
        super().__init__()
        self.fig = plt.figure(figsize=kwargs['figsize'], dpi=100, facecolor="white")
        self.graph_dict = {}
        self.graph_curr = []

        gs = gridspec.GridSpec(
            kwargs['nrows'], kwargs['ncols'], 
            left=kwargs['left'], bottom=kwargs['bottom'], 
            right=kwargs['right'], top=kwargs['top'], 
            wspace=kwargs['wspace'], hspace=kwargs['hspace'], 
            height_ratios=kwargs['height_ratios']
        )
        for i in range(0, kwargs['nrows'], 1):
            self.graph_dict[kwargs['subplots'][i]] = self.fig.add_subplot(gs[i, :])

    def log_trade_info(self, stock_dat):
        signal_shift = stock_dat.Signal.shift(1).fillna(-1)
        diff_signal = stock_dat.Signal - signal_shift

        buy_signal = stock_dat[diff_signal == 2]
        sell_signal = stock_dat[diff_signal == -2]

        min_len = min(len(buy_signal), len(sell_signal))
        if min_len == 0:
            print("No completed trade pair found.")
            return

        buy_signal = buy_signal.iloc[:min_len]
        sell_signal = sell_signal.iloc[:min_len]

        trade_info = pd.DataFrame({
            'BuyTime': buy_signal.index.strftime('%Y-%m-%d'),
            'SellTime': sell_signal.index.strftime('%Y-%m-%d'),
            'BuyPrice': buy_signal.Close.values,
            'SellPrice': sell_signal.Close.values
        })

        trade_info['DiffPrice'] = trade_info.SellPrice - trade_info.BuyPrice
        trade_info['PctProfit'] = np.round(trade_info.DiffPrice / trade_info.BuyPrice * 100, 2)

        print(trade_info)

    def graph_run(self, stock_data, **kwargs):
        self.df_ohlc = stock_data
        self.log_trade_info(self.df_ohlc)
        for key in kwargs:
            self.graph_curr = self.graph_dict[kwargs[key]['graph_name']]
            for path, val in kwargs[key]['graph_type'].items():
                view_function = MultiTraceIf.app.route_output(path)
                view_function(self.df_ohlc, self.graph_curr, val)
            self.graph_attr(**kwargs[key])
        plt.show()

    def graph_attr(self, **kwargs):
        if 'title' in kwargs:
            self.graph_curr.set_title(kwargs['title'], fontsize=11, fontweight='bold')
        if 'legend' in kwargs:
            self.graph_curr.legend(loc=kwargs['legend'], shadow=True)
        if 'xlabel' in kwargs:
            self.graph_curr.set_xlabel(kwargs['xlabel'])

        self.graph_curr.set_ylabel(kwargs['ylabel'])
        self.graph_curr.set_xlim(0, len(self.df_ohlc.index))
        
        step = kwargs.get('xticks', 15)
        self.graph_curr.set_xticks(range(0, len(self.df_ohlc.index), step))

        if 'xticklabels' in kwargs:
            formatted_dates = self.df_ohlc.index.strftime(kwargs['xticklabels'])
            self.graph_curr.set_xticklabels(
                [formatted_dates[i] for i in self.graph_curr.get_xticks()]
            )
            for label in self.graph_curr.xaxis.get_ticklabels():
                label.set_rotation(45)
                label.set_fontsize(9)
        else:
            for label in self.graph_curr.xaxis.get_ticklabels():
                label.set_visible(False)