import numpy as np
import matplotlib.pyplot as plt
from MplVisualIf import MplTypesDraw, DefTypesPool

class MultiGraphIf(MplTypesDraw):
    app = DefTypesPool()

    def __init__(self, stock_dat, **layout_dict):
        super().__init__()
        self.stock_dat = stock_dat
        self.layout_dict = layout_dict

    @app.route_types("ochl")
    def och1_graph(self, stock_dat, sub_graph, df_dat = None):
        type_dict = {
            'Open': stock_dat.Open, 
            'Close': stock_dat.Close,
            'High': stock_dat.High, 
            'Low': stock_dat.Low
        }
        view_function = MplTypesDraw.mpl.route_output("ochl")
        view_function(stock_dat.index, type_dict, sub_graph)

    @app.route_types("sma")
    def sma_graph(self, stock_dat, sub_graph, periods):
        for val in periods:
            type_dict = {'SMA' + str(val): stock_dat.Close.rolling(window=val).mean()}
            view_function = MplTypesDraw.mpl.route_output("line")
            view_function(stock_dat.index, type_dict, sub_graph)

    @app.route_types("vol")
    def vol_graph(self, stock_dat, sub_graph, df_dat = None):
        type_dict = {
            'bar_red': np.where(stock_dat.Open < stock_dat.Close, stock_dat.Volume, 0),
            'bar_green': np.where(stock_dat.Open >= stock_dat.Close, stock_dat.Volume, 0),
        }
        view_function = MplTypesDraw.mpl.route_output("bar")
        view_function(stock_dat.index, type_dict, sub_graph)

    @app.route_types("macd")
    def macd_graph(self, stock_dat, sub_graph, df_dat = None):
        macd_dif = stock_dat['Close'].ewm(span=12, adjust=False).mean() - stock_dat['Close'].ewm(span=26, adjust=False).mean()
        macd_dea = macd_dif.ewm(span=9, adjust=False).mean()
        macd_bar = 2 * (macd_dif - macd_dea)

        bar_dict = {
            'bar_red': np.where(macd_bar > 0, macd_bar, 0),
            'bar_green': np.where(macd_bar < 0, macd_bar, 0)
        }
        MplTypesDraw.mpl.route_output("bar")(stock_dat.index, bar_dict, sub_graph)

        line_dict = {'macd dif': macd_dif, 'macd dea': macd_dea}
        MplTypesDraw.mpl.route_output("line")(stock_dat.index, line_dict, sub_graph)

    @app.route_types("kdj")
    def kdj_graph(self, stock_dat, sub_graph, df_dat = None):
        low_list = stock_dat['Low'].rolling(9, min_periods=1).min()
        high_list = stock_dat['High'].rolling(9, min_periods=1).max()
        rsv = (stock_dat['Close'] - low_list) / (high_list - low_list) * 100
        K = rsv.ewm(com=2, adjust=False).mean()
        D = K.ewm(com=2, adjust=False).mean()
        J = 3 * K - 2 * D

        type_dict = {'K': K, 'D': D, 'J': J}
        MplTypesDraw.mpl.route_output("line")(stock_dat.index, type_dict, sub_graph)

    def graph_run(self, subplots_dict):
        nrows = self.layout_dict.get('nrows', 1)
        figsize = tuple(self.layout_dict.get('figsize', (12, 8)))
        height_ratios = self.layout_dict.get('height_ratios', [1]*nrows)

        fig, axes = plt.subplots(nrows, 1, figsize=figsize, sharex=True, gridspec_kw={'height_ratios': height_ratios})
        if nrows == 1:
            axes = [axes]

        for i, (key, sub_cfg) in enumerate(subplots_dict.items()):
            ax = axes[i]
            for draw_type, params in sub_cfg['graph_type'].items():
                handler = self.app.route_output(draw_type)
                handler(self, self.stock_dat, ax, params)

            if 'ylabel' in sub_cfg:
                ax.set_ylabel(sub_cfg['ylabel'])
            if 'legend' in sub_cfg:
                ax.legend(loc=sub_cfg['legend'])

        step = 15
        axes[-1].set_xticks(range(0, len(self.stock_dat.index), step))
        formatted_dates = self.stock_dat.index.strftime('%Y-%m-%d')
        axes[-1].set_xticklabels([formatted_dates[j] for j in axes[-1].get_xticks()], rotation=45)
        
        plt.tight_layout()
        plt.show()