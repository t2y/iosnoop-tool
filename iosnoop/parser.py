import re
from collections import defaultdict
from datetime import timedelta

from .consts import EXTRA_COLUMNS
from .consts import PROCESS_ID, DISK_BLOCK, IO_SIZE, IO_LATENCY
from .consts import START_TIME_STAMP, END_TIME_STAMP
from .consts import START_TIME_STAMP_DIFF, START_LOCAL_TIME

from .filters import get_filters
from .utils import get_logger

log = get_logger()

_IOSNOOP_DATA_TYPE = defaultdict(lambda: lambda x: x)
_IOSNOOP_DATA_TYPE[PROCESS_ID] = int
_IOSNOOP_DATA_TYPE[DISK_BLOCK] = int
_IOSNOOP_DATA_TYPE[IO_SIZE] = int
_IOSNOOP_DATA_TYPE[START_TIME_STAMP] = float
_IOSNOOP_DATA_TYPE[END_TIME_STAMP] = float
_IOSNOOP_DATA_TYPE[IO_LATENCY] = float

_IOSNOOP_LOG_DESCRIPTION = re.compile(r'tracing', re.IGNORECASE)


class Parser:

    def __init__(self, args):
        self.args = args
        self._columns = None
        self.first_row = None
        self.filters = get_filters(args)

    @property
    def columns(self):
        extra = EXTRA_COLUMNS.copy()
        if self.args.basedate is None:
            extra.remove(START_LOCAL_TIME)
        return self._columns + extra

    def _get_time_diff(self, row):
        if self.first_row is None:
            return 0
        return row[START_TIME_STAMP] - self.first_row[START_TIME_STAMP]

    def _get_local_time(self, row):
        diff = row[START_TIME_STAMP_DIFF]
        return self.args.basedate + timedelta(seconds=diff)

    def _parse(self, line):
        if line == '\n':
            return

        data = line.strip().split()
        try:
            float(data[0])  # check whether data row or not
        except ValueError:
            log.debug(line.strip())
            if re.search(_IOSNOOP_LOG_DESCRIPTION, line):
                return  # description

            # expects header if line is not description
            self._columns = data
            return
        else:
            row = {}
            for i, col in enumerate(self._columns):
                type_factory = _IOSNOOP_DATA_TYPE[col]
                row[col] = type_factory(data[i])
            row[START_TIME_STAMP_DIFF] = self._get_time_diff(row)
            if self.args.basedate is not None:
                row[START_LOCAL_TIME] = self._get_local_time(row)

            if row:
                if self.first_row is None:
                    self.first_row = row
                yield row

    def filter(self, row):
        for filter_func in self.filters:
            if not filter_func(row):
                return False
        return True

    def parse(self):
        with open(self.args.data) as f:
            for line in f:
                for row in self._parse(line):
                    if self.filter(row):
                        yield row
