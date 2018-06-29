import textwrap

import pandas as pd

from .consts import COMMAND, PROCESS_ID, IO_TYPE, DEVICE_ID, IO_SIZE
from .consts import PLOT_TYPE_HEATMAP
from .heatmap import HeatMap
from .parser import Parser
from .utils import get_logger

log = get_logger()


_SHOW_MAX_UNIQUE_VALUES = 50


def show_unique_values(df):
    columns = [COMMAND, PROCESS_ID, IO_TYPE, DEVICE_ID, IO_SIZE]
    for column in columns:
        unique_num = df[column].nunique()
        message = '%s column has %d values' % (column, unique_num)
        if unique_num <= _SHOW_MAX_UNIQUE_VALUES:
            lines = '\n'.join(str(i) for i in df[column].unique())
            values = textwrap.indent(lines, prefix='  - ')
            message += ' and they are as below\n%s' % values
        log.info(message)


def show_data_info(df):
    show_unique_values(df)


def plot_data(args):
    parser = Parser(args)
    rows = [row for row in parser.parse()]
    if len(rows) == 0:
        log.info('no rows, so heatmap will not create')
        return

    df = pd.DataFrame(rows, columns=parser.columns)
    show_data_info(df)

    if args.plot_type == PLOT_TYPE_HEATMAP:
        heatmap = HeatMap(args, df)
        heatmap.render()
