import pandas as pd

from pydruid.client import *
from pydruid.utils.filters import Dimension


druid = PyDruid('http://10.129.34.90:8082', 'druid/v2')


def list_bus_lines(date):
    if not date:
        return {}

    query = druid.groupby(
        datasource='bus_data',
        granularity='all',
        intervals=date + '/p1d',
        dimensions=['line', 'order']
    )
    df = query.export_pandas()
    return df.groupby('line').apply(lambda d: d['order'].to_list()).to_dict()


def get_bus_positions(line, order, date):
    query = druid.scan(
        datasource='bus_data',
        granularity='all',
        intervals=date + '/p1d',
        filter=((Dimension("line") == line) & (Dimension("order") == order)),
        columns=["__time", "datetimeDiff", "distance", "latitude", "longitude"]
    )
    df = query.export_pandas()
    df = df[df['datetimeDiff'] <= (5 * 60)]
    df['speed'] = (df['distance'] / df['datetimeDiff'] * 3.6).round(0).astype('Int64').astype('str') + ' Km/h'
    df['datetime'] = pd.to_datetime(df['__time'], unit='ms', origin='unix')

    print(df)

    return df.drop(columns=['__time', 'datetimeDiff', 'distance'])

