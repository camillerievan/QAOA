from enum import Enum
import pandas as pd
from matplotlib.patches import Rectangle

# define constants
box_alpha = 0.2  # Opacity
bar_width = 0.15  # Width of all bars
max_y = None
do_thousands_formatter = None

class DataSegmentType(Enum):
    MA = ('red', {'color': 'red', 'marker': 's', 'markersize': 10})
    AM = ('green', {'color': 'green', 'marker': '^', 'markersize': 10})
    KA = ('orange', {'color': 'orange', 'marker': 'o', 'markersize': 10})
    SA = ('blue', {'color': 'blue', 'marker': 'D', 'markersize': 10})

    def __init__(self, facecolor, indicator):
        self.facecolor = facecolor
        self.indicator = indicator


class ClassicalAlgorithm(Enum):
    All = -1
    BFGS = 1
    POWELL = 2


class GraphResultType(Enum):
    AR = 1
    CC = 2
    AP = 3


class GraphType(Enum):
    All = -1
    Path = 1
    Cyclic = 2


class InitialAngle(Enum):
    All = -1
    F1P = 0
    R01P = 3
    R02PIP = 4
    TQA = 8


class AngleType(Enum):
    MultiAngle = 'ma'
    KAngle = 'ka'
    AutomorphicAngle = 'am'
    SingleAngle = 'sa'

def plot_data_segment(ax, data, segment_type):
    """
    Plots high/low lines and open/close boxes for the given dataset, and overlays the average line.

    Parameters:
    - ax: Matplotlib Axes object to plot on.
    - data: Pandas DataFrame containing the data.
    - segment_type: DataSegmentType Enum member indicating the data segment to plot.
    - max_y: Maximum y-value for scaling; if -1, no scaling is applied.
    - bar_width: Width of the open/close rectangle.
    - box_alpha: Transparency level for the rectangle.
    """
    if data is not None:
        facecolor = segment_type.facecolor
        indicator = segment_type.indicator

        for _, row in data.iterrows():
            date = row['n']
            open_price = row['average'] - row['stdev']

            # Determine close_price based on max_y
            if max_y == -1:
                close_price = row['average'] + row['stdev']
            else:
                close_price = min(row['average'] + row['stdev'], max_y)

            low = row['min']
            high = row['max']

            # Plot high/low lines
            ax.plot([date, date], [low, high], color='black', lw=1.5)

            # Plot open/close rectangle
            rect = Rectangle(
                (date - bar_width / 2, min(open_price, close_price)),
                bar_width,
                abs(open_price - close_price),
                facecolor=facecolor,
                edgecolor='black',
                alpha=box_alpha
            )
            ax.add_patch(rect)

        # Prepare keyword arguments for the average line plot
        plot_kwargs = {
            'color': indicator.get('color', 'black'),
            'marker': indicator.get('marker', 'o'),
            'markersize': indicator.get('markersize', 5)
        }

        # Optionally include markerfacecolor if provided
        if 'markerfacecolor' in indicator:
            plot_kwargs['markerfacecolor'] = indicator['markerfacecolor']

        # Adjust line weight for KA (orange)
        if segment_type == DataSegmentType.KA:
            plot_kwargs['lw'] = 2.5  # Increase line width

        # Overlay the average line
        ax.plot(data['n'], data['average'], **plot_kwargs)

# load data
def load_data(file_name):
    # todo: load data from database
    try:
        return pd.read_csv(file_name)
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        return None

#formatter
def thousands_formatter(x, pos):
    if do_thousands_formatter == 1000:
        return f'{int(x/1000)}k'
    elif do_thousands_formatter == 1:
        return f'{round(x, 1):g}'
    else:
        return f'{x:g}'
