PACKAGE_NAME = 'iosnoop-tool'

# parser options
SUB_COMMAND_CSV = 'csv'
SUB_COMMAND_PLOT = 'plot'

# plot options
PLOT_TYPE_HEATMAP = 'heatmap'
PLOT_TYPES = [
    PLOT_TYPE_HEATMAP,
]

# iosnoop columns
START_TIME_STAMP = 'STARTs'
END_TIME_STAMP = 'ENDs'
COMMAND = 'COMM'
PROCESS_ID = 'PID'
IO_TYPE = 'TYPE'
DEVICE_ID = 'DEV'
DISK_BLOCK = 'BLOCK'
IO_SIZE = 'BYTES'
IO_LATENCY = 'LATms'
# extra columns
START_TIME_STAMP_DIFF = 'STARTs_DIFF'
START_LOCAL_TIME = 'STARTs_LOCAL_TIME'
EXTRA_COLUMNS = [
    START_TIME_STAMP_DIFF,
    START_LOCAL_TIME,
]

# dataframe bin columns
LATENCY_BINS = 'latency_bins'
TS_DIFF_BINS = 'ts_diff_bins'
LOCAL_TIME_BINS = 'local_time_bins'
