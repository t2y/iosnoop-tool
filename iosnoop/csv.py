import csv
from contextlib import ContextDecorator

from .parser import Parser
from .utils import make_output_file


class Writer(ContextDecorator):

    def __init__(self, args):
        self.args = args
        self.f = open(self.output, 'w')
        self.writer = csv.writer(
            self.f, dialect=args.dialect, delimiter=args.separator,
            quoting=csv.QUOTE_MINIMAL
        )

    @property
    def output(self):
        output = self.args.output
        if output is None:
            output = make_output_file(self.args.data, 'csv')
        return output

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.f.close()

    def write_header(self, columns):
        headers = columns
        if self.args.columns:
            headers = self.args.columns
        self.writer.writerow(headers)

    def write(self, row):
        row = list(row)  # for py34 compatibility
        self.writer.writerow(row)


def write_csv(args):
    parser = Parser(args)
    with Writer(args) as f:
        g = parser.parse()
        try:
            first_row = next(g)
        except StopIteration:
            return
        else:
            f.write_header(parser.columns)
            f.write(first_row.values())
            for row in g:
                f.write(row.values())
