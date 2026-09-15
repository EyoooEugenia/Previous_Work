import numpy as np
import matplotlib.pyplot as plt
import mplfinance.original_flavor as mpf

class DefTypesPool():
    def __init__(self):
        self.routes = {}

    def route_types(self, types_str):
        def decorator(f):
            self.routes[types_str] = f
            return f
        return decorator

    def route_output(self, path):
        function_val = self.routes.get(path)
        if function_val:
            return function_val
        else:
            raise ValueError('Route "{}" has not been registered'.format(path))


class MplTypesDraw():
    mpl = DefTypesPool()

    @mpl.route_types(u"line")
    def line_plot(df_index, df_dat, graph):
        for key, val in df_dat.items():
            graph.plot(np.arange(0, len(val)), val, label=key, lw=1.0)

    @mpl.route_types(u"ochl")
    def och1_plot(df_index, df_dat, graph):
        mpf.candlestick2_ochl(
            graph, df_dat['Open'], df_dat['Close'], 
            df_dat['High'], df_dat['Low'], 
            width=0.5, colorup='r', colordown='g'
        )

    @mpl.route_types(u"bar")
    def bar_plot(df_index, df_dat, graph):
        graph.bar(np.arange(0, len(df_index)), df_dat['bar_red'], facecolor='red', label='Up')
        graph.bar(np.arange(0, len(df_index)), df_dat['bar_green'], facecolor='green', label='Down')

    @mpl.route_types(u"annotate")
    def annotate_plot(df_index, df_dat, graph):
        for key, val in df_dat.items():
            for k1_index, today in val['andata'].iterrows():
                x_posit = df_index.get_loc(k1_index)
                graph.annotate(
                    u"{}\n{}".format(key, today.name.strftime("%m.%d")), 
                    xy=(x_posit, today[val['xy_y']]), 
                    xycoords='data', 
                    xytext=(val['xytext'][0], val['xytext'][1]), 
                    va=val.get('va', 'bottom'), 
                    textcoords='offset points', 
                    fontsize=val['fontsize'], 
                    arrowprops=val['arrow']
                )

    @mpl.route_types(u"hline")
    def hline_plot(df_index, df_dat, graph):
        for key, val in df_dat.items():
            graph.axhline(val['pos'], c=val['c'], label=key)


class MplVisualIf(MplTypesDraw):
    def __init__(self):
        super().__init__()

    def fig_creat(self, **kwargs):
        figsize = kwargs.get('figsize', (14, 7))
        self.fig = plt.figure(figsize=figsize, dpi=100, facecolor="white")
        self.graph = self.fig.add_subplot(1, 1, 1)
        self.fig.autofmt_xdate(rotation=45)

    def fig_config(self, **kwargs):
        if 'legend' in kwargs:
            self.graph.legend(loc=kwargs['legend'], shadow=True)
            
        self.graph.set_xlabel(kwargs.get('xlabel', 'Date'))
        
        if 'title' in kwargs:
            self.graph.set_title(kwargs['title'])
            
        if 'ylabel' in kwargs:
            self.graph.set_ylabel(kwargs['ylabel'])
            
        self.graph.set_xlim(0, len(self.index))

        if 'ylim' in kwargs:
            bottom_lim, top_lim = self.graph.get_ylim()
            range_lim = top_lim - bottom_lim
            self.graph.set_ylim(
                bottom_lim + range_lim * kwargs['ylim'][0], 
                top_lim + range_lim * kwargs['ylim'][1]
            )

        step = kwargs.get('xticks', 15)
        self.graph.set_xticks(range(0, len(self.index), step))

        date_format = kwargs.get('xticklabels', '%Y-%m-%d')
        formatted_dates = self.index.strftime(date_format)
        self.graph.set_xticklabels([formatted_dates[i] for i in self.graph.get_xticks()])

    def fig_show(self, **kwargs):
        plt.show()

    def fig_output(self, **kwargs):
        self.index = kwargs['index']
        self.fig_creat(**kwargs)
        for path, val in kwargs['draw_kind'].items():
            print("output [%s] visual graph:" % path)
            view_function = self.mpl.route_output(path)
            view_function(self.index, val, self.graph)
        self.fig_config(**kwargs)
        self.fig_show(**kwargs)