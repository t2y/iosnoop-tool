from datetime import datetime, timedelta
from functools import lru_cache

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .consts import COMMAND, PROCESS_ID, IO_TYPE, DEVICE_ID
from .consts import IO_LATENCY, START_TIME_STAMP_DIFF, START_LOCAL_TIME
from .consts import LATENCY_BINS, TS_DIFF_BINS, LOCAL_TIME_BINS
from .utils import get_logger, make_output_file

sns.set()
log = get_logger()


class HeatMap:

    def __init__(self, args, df):
        self.args = args
        self.df = df
        self.df[LATENCY_BINS] = pd.cut(
            self.df[IO_LATENCY], bins=self.io_latency_bins, right=False)

        if self.args.basedate is None:
            self.df[TS_DIFF_BINS] = pd.cut(
                self.df[START_TIME_STAMP_DIFF],
                bins=self.time_stamp_bins, right=False)
        else:
            self.df[LOCAL_TIME_BINS] = pd.cut(
                self.df[START_LOCAL_TIME],
                bins=self.local_time_bins, right=False)

        self.fig = plt.figure(figsize=self.figsize)
        self.fig.suptitle(self.subtitle)

    @property
    @lru_cache(1)
    def output(self):
        output = self.args.figoutput
        if output is None:
            output = make_output_file(self.args.data, 'png')
        return output

    @property
    @lru_cache(1)
    def figsize(self):
        figsize = self.args.figsize
        if figsize is None:
            figsize = (10.24, 8)
        return figsize

    @property
    @lru_cache(1)
    def subtitle(self):
        title = 'block i/o traced by iosnoop'
        filtered = []
        if len(self.args.io_commands) > 0:
            commands = ', '.join(self.args.io_commands)
            filtered.append('%s: %s' % (COMMAND, commands))
        if self.args.io_device is not None:
            filtered.append('%s: %s' % (DEVICE_ID, self.args.io_device))
        if len(self.args.io_pids) > 0:
            pids = ', '.join(str(i) for i in self.args.io_pids)
            filtered.append('%s: %s' % (PROCESS_ID, pids))
        if len(self.args.io_types) > 0:
            types_ = ', '.join(self.args.io_types)
            filtered.append('%s: %s' % (IO_TYPE, types_))
        if len(filtered) > 0:
            title += ', filtered by %s' % ', '.join(filtered)
        return title

    @property
    @lru_cache(1)
    def max_io_latency(self):
        if self.args.y_max is not None:
            return self.args.y_max
        return self.df[IO_LATENCY].max()

    @property
    @lru_cache(1)
    def io_latency_bins(self):
        max_latency = self.max_io_latency
        log.info('maximum io latency: %f', max_latency)
        freq = self.args.y_interval
        if freq > max_latency:
            freq = max_latency / 10
        return pd.interval_range(
            start=0.0, end=max_latency + (2 * freq), freq=freq, closed='left')

    @property
    @lru_cache(1)
    def max_time_stamp_diff(self):
        if self.args.x_max is not None:
            return self.args.x_max
        return self.df[START_TIME_STAMP_DIFF].max()

    @property
    @lru_cache(1)
    def time_stamp_bins(self):
        max_diff = self.max_time_stamp_diff
        log.info('maximum time stamp diff: %f', max_diff)
        freq = self.args.x_interval
        if freq > max_diff:
            freq = max_diff / 100
        return pd.interval_range(
            start=0.0, end=max_diff + freq, freq=freq, closed='left')

    @property
    @lru_cache(1)
    def max_local_time(self):
        if self.args.x_max is not None:
            x_max = timedelta(seconds=self.args.x_max)
            return self.df[START_LOCAL_TIME][0] + x_max
        return self.df[START_LOCAL_TIME].max()

    @property
    @lru_cache(1)
    def local_time_bins(self):
        max_time = self.max_local_time
        log.info('maximum localtime: %s', max_time)
        freq = timedelta(seconds=self.args.x_interval)
        if self.args.basedate + freq > max_time:
            interval = self.args.x_interval / 100
            freq = timedelta(seconds=interval)
        return pd.interval_range(
            start=self.args.basedate, end=max_time + freq, freq=freq,
            closed='left')

    def reshape_data(self, df):
        if self.args.basedate is None:
            columns_bins = TS_DIFF_BINS
            columns = self.time_stamp_bins
        else:
            columns_bins = LOCAL_TIME_BINS
            columns = self.local_time_bins

        pivot = df.pivot_table(
            index=LATENCY_BINS, columns=columns_bins, values=IO_LATENCY,
            aggfunc='count',
        ).reindex(
            index=self.io_latency_bins, columns=columns,
        )
        if self.args.verbose:
            print(pivot)
        return pivot

    @staticmethod
    def simplify_label(label):
        text = label.get_text()
        return text.split(',')[0].replace('[', '')

    @staticmethod
    def simplify_local_time(label):
        text = label.get_text()
        time_str = text.split(',')[0].replace('[', '').split()
        if len(time_str) == 1:
            return '00:00:00'
        else:
            return time_str[1]

    def set_axes(self, ax, title=None):
        ax.invert_yaxis()
        ax.set_title(title)

        xlabel = 'time (second)'
        xticklabels = ax.get_xticklabels()
        if self.args.basedate is None:
            ax.set_xlabel(xlabel)
            ax.set_xticklabels(map(self.simplify_label, xticklabels))
        else:
            date_str = datetime.strftime(self.args.basedate, '%Y-%m-%d')
            ax.set_xlabel(xlabel + '\n%s' % date_str)
            ax.set_xticklabels(map(self.simplify_local_time, xticklabels))

        ax.set_ylabel('latency (millisecond)')
        ax.set_yticklabels(map(self.simplify_label, ax.get_yticklabels()))
        ax.xaxis.set_label_coords(1.10, -0.05)

    def make_heatmap(self, df, ax, vmax, title=None):
        hm_ax = sns.heatmap(
            df,
            ax=ax,
            cmap=self.args.colormap,
            square=self.args.square,
            vmax=vmax,
            xticklabels=10,
        )
        self.set_axes(hm_ax, title)
        return hm_ax

    def generate_latency_heatmaps(self):
        rows = len(self.args.subplot_conditions) + 1
        normal = self.fig.add_subplot(rows, 1, 1)
        normal_data = self.reshape_data(self.df)
        vmax = normal_data.fillna(0).values.max()
        self.make_heatmap(normal_data, normal, vmax, 'Normal')

        for i, cond in enumerate(self.args.subplot_conditions, 2):
            df = self.df[eval('self.df.' + cond)]
            if len(df) == 0:
                log.warn('no data with condition: %s', cond)
                continue
            ax = self.fig.add_subplot(rows, 1, i)
            data = self.reshape_data(df)
            self.make_heatmap(data, ax, vmax, cond)

    def render(self):
        self.generate_latency_heatmaps()
        plt.subplots_adjust(hspace=self.args.hspace)
        if self.args.backend == 'Agg':
            self.fig.savefig(self.output)
        else:
            plt.show()
