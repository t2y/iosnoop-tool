import argparse
import csv
import logging

from .consts import PLOT_TYPES, PLOT_TYPE_HEATMAP
from .consts import SUB_COMMAND_CSV, SUB_COMMAND_PLOT
from .csv import write_csv
from .utils import get_logger, parse_datetime

__version__ = '0.1.0'
_DATETIME_FORMAT_HELP = 'yyyymmddHHMISS'

_COMMA = 'comma'
_TAB = 'tab'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
)
log = get_logger()


def dt_type(s):
    return parse_datetime(s)


def figsize_type(s):
    values = s.split(',')
    if len(values) != 2:
        msg = 'set width and height in inches, e.g.) "6.4, 4.8"'
        raise argparse.ArgumentTypeError(msg)
    return tuple(float(i.strip()) for i in values)


def sep_type(s):
    if s == _COMMA:
        return ','
    elif s == _TAB:
        return '\t'
    else:
        raise argparse.ArgumentTypeError('separator is wrong')


def parse_csv_argument(subparsers):
    csv_parser = subparsers.add_parser(SUB_COMMAND_CSV)
    csv_parser.set_defaults(
        dialect='excel',
        output=None,
        separator=_COMMA,
    )
    csv_parser.add_argument(
        '--dialect', action='store', choices=csv.list_dialects(),
        help='set dialect for csv writer, default is excel'
    )
    csv_parser.add_argument(
        '--output', action='store',
        help='set path to save csv file of iosnoop',
    )
    csv_parser.add_argument(
        '--separator', action='store', type=sep_type,
        help='set separator (choose from comma, tab), default is comma'
    )


def parse_plot_argument(subparsers):
    plot_parser = subparsers.add_parser(SUB_COMMAND_PLOT)
    plot_parser.set_defaults(
        backend='Agg',
        colormap='Reds',
        figoutput=None,
        figsize=None,
        hspace=0.6,
        square=False,
        subplot_conditions=[],
        x_interval=1.0,
        x_max=None,
        y_interval=50.0,
        y_max=None,
        plot_type=PLOT_TYPE_HEATMAP,
    )
    plot_parser.add_argument(
        '--backend', action='store',
        help='set backend for matplotlib, '
             'use TkAgg to monitor in the foreground',
    )
    plot_parser.add_argument(
        '--colormap', action='store',
        help='set color map for seaborn heatmap'
    )
    plot_parser.add_argument(
        '--fig-output', action='store', dest='figoutput',
        help='set path to save graph'
    )
    plot_parser.add_argument(
        '--fig-size', action='store', dest='figsize', type=figsize_type,
        help='set figure size'
    )
    plot_parser.add_argument(
        '--hspace', action='store', type=float,
        help='set hspace for subplot'
    )
    plot_parser.add_argument(
        '--plot-type', action='store', dest='plot_type', choices=PLOT_TYPES,
        help='set plot type ("%s" by default) ' % PLOT_TYPE_HEATMAP
    )
    plot_parser.add_argument(
        '--square', action='store_true',
        help='set square mode for heatmap'
    )
    plot_parser.add_argument(
        '--subplot-conditions', dest='subplot_conditions', action='store',
        nargs='+', type=lambda s: s.strip(),
        help='set DataFrame conditions to filter',
    )
    plot_parser.add_argument(
        '--x-interval', action='store', dest='x_interval', type=float,
        help='set value of interval for x bins'
    )
    plot_parser.add_argument(
        '--x-max', action='store', dest='x_max', type=float,
        help='set maximum value for x-axis'
    )
    plot_parser.add_argument(
        '--y-interval', action='store', dest='y_interval', type=float,
        help='set value of interval for y bins'
    )
    plot_parser.add_argument(
        '--y-max', action='store', dest='y_max', type=float,
        help='set maximum value for y-axis'
    )


def parse_argument():
    parser = argparse.ArgumentParser()
    parser.set_defaults(
        basedate=None,
        data=None,
        # filter options
        columns=[],
        io_commands=[],
        io_device=None,
        io_pids=[],
        io_types=[],
        since=None,
        until=None,
        subcommand=None,
    )
    parser.add_argument(
        '--basedate', action='store', type=dt_type,
        help='set base datetime to convert kernel timestamp to localtime,'
             ' format: %s' % _DATETIME_FORMAT_HELP
    )
    parser.add_argument(
        '--data', action='store', required=True,
        help='set path to iosnoop output file',
    )

    # filter options
    parser.add_argument(
        '--columns', action='store', nargs='+',
        help='set columns name in iosnoop output'
    )
    parser.add_argument(
        '--io-commands', dest='io_commands', action='store', nargs='+',
        help='set commands in iosnoop output',
    )
    parser.add_argument(
        '--io-device', dest='io_device', action='store',
        help='set device in iosnoop output',
    )
    parser.add_argument(
        '--io-pids', dest='io_pids', action='store', nargs='+', type=int,
        help='set process ids in iosnoop output',
    )
    parser.add_argument(
        '--io-types', dest='io_types', action='store', nargs='+',
        help='set types in iosnoop output',
    )
    parser.add_argument(
        '--since', action='store', type=float,
        help='set seconds since relative difference from start'
    )
    parser.add_argument(
        '--until', action='store', type=float,
        help='set seconds until relative difference from start'
    )
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    parse_csv_argument(subparsers)
    parse_plot_argument(subparsers)

    # for debug
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='set verbose mode'
    )
    parser.add_argument(
        '--version', action='version', version='%%(prog)s %s' % __version__,
        help='show program version',
    )

    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    return args


def main():
    args = parse_argument()
    log.debug(args)

    if args.subcommand == SUB_COMMAND_CSV:
        write_csv(args)
    elif args.subcommand == SUB_COMMAND_PLOT:
        import matplotlib
        matplotlib.use(args.backend)
        from .plotter import plot_data
        plot_data(args)


if __name__ == '__main__':
    main()
