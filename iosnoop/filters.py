from functools import partial

from .consts import COMMAND, PROCESS_ID, IO_TYPE, DEVICE_ID
from .consts import START_TIME_STAMP, START_TIME_STAMP_DIFF


def filter_since(since, row):
    return since <= row[START_TIME_STAMP_DIFF]


def filter_until(until, row):
    return row[START_TIME_STAMP_DIFF] <= until


def filter_columns(columns_names, row):
    if START_TIME_STAMP not in columns_names:
        columns_names.insert(0, START_TIME_STAMP)

    excludes = [name for name in row if name not in columns_names]
    for name in excludes:
        del row[name]
    return True


def filter_io_commands(commands, row):
    for command in commands:
        if command in row[COMMAND]:
            return True
    return False


def filter_io_device(device, row):
    return row[DEVICE_ID] == device


def filter_io_pids(pids, row):
    return row[PROCESS_ID] in pids


def filter_io_types(io_types, row):
    return row[IO_TYPE] in io_types


def get_filters(args):
    filters = []
    if args.since is not None:
        filters.append(partial(filter_since, args.since))
    if args.until is not None:
        filters.append(partial(filter_until, args.until))
    if args.columns:
        filters.append(partial(filter_columns, args.columns))
    if args.io_commands:
        filters.append(partial(filter_io_commands, args.io_commands))
    if args.io_device:
        filters.append(partial(filter_io_device, args.io_device))
    if args.io_pids:
        filters.append(partial(filter_io_pids, args.io_pids))
    if args.io_types:
        filters.append(partial(filter_io_types, args.io_types))

    return filters
