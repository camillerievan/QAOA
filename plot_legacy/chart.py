import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

# =========================================================
# CONFIG — set MODE to 'AR', 'AP', or 'NFEV'
# =========================================================
MODE = 'NFEV'

export_path = 'C:\\Bikini Atoll\\QUANTUM\\BACKUP 20251120\\projects\\ex09\\_out20260228\\_graph\\_dissertation_charts\\'

if MODE == 'AR':
    prefix       = 'ar-d-'
    y_axis_title = 'AR'
    max_y        = 1
    yscale       = 1
    figwidth     = 12.5
elif MODE == 'AP':
    prefix       = 'ap-d-'
    y_axis_title = r'$F$'
    max_y        = 100
    yscale       = 1
    figwidth     = 12.5
elif MODE == 'NFEV':
    prefix       = 'c-'
    y_axis_title = r'nfev ($\times 10^3$)'
    max_y        = -1
    yscale       = 1000
    figwidth     = 13

bar_width = 0.15
box_alpha  = 0.2

ma_indicator = {'color': 'red',    'marker': 's', 'markersize': 5}
am_indicator = {'color': 'green',  'marker': '^', 'markersize': 5}
ka_indicator = {'color': 'orange', 'marker': 'o', 'markersize': 5, 'markerfacecolor': 'none'}
sa_indicator = {'color': 'blue',   'marker': 'o', 'markersize': 5, 'markerfacecolor': 'blue'}


def load_data(file_name):
    try:
        return pd.read_csv(file_name)
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        return None


def plot_series(ax, data, facecolor, indicator):
    if data is None:
        return

    for _, row in data.iterrows():
        date  = row['n']
        avg   = row['average'] / yscale
        stdev = row['stdev']   / yscale
        low   = row['min']     / yscale
        high  = row['max']     / yscale

        open_price  = avg - stdev
        close_price = avg + stdev if max_y == -1 else min(avg + stdev, max_y / yscale)

        ax.plot([date, date], [low, high], color='black', lw=1.5)
        ax.add_patch(Rectangle(
            (date - bar_width / 2, min(open_price, close_price)),
            bar_width, abs(open_price - close_price),
            facecolor=facecolor, edgecolor='black', alpha=box_alpha,
        ))

    extra = {k: v for k, v in indicator.items() if k == 'markerfacecolor'}
    ax.plot(
        data['n'], data['average'] / yscale,
        color=indicator['color'],
        marker=indicator['marker'],
        markersize=indicator['markersize'],
        **extra,
    )


data_ma = load_data(f'{prefix}data-ma.csv')
data_am = load_data(f'{prefix}data-am.csv')
data_ka = load_data(f'{prefix}data-ka.csv')
data_sa = load_data(f'{prefix}data-sa.csv')

fig, ax1 = plt.subplots(figsize=(figwidth, 7.6))

plot_series(ax1, data_ma, 'red',    ma_indicator)
plot_series(ax1, data_am, 'green',  am_indicator)
plot_series(ax1, data_ka, 'orange', ka_indicator)
plot_series(ax1, data_sa, 'blue',   sa_indicator)

if data_ma is not None:
    ax1.set_xticks(data_ma['n'])
    ax1.set_xticklabels(data_ma['n'], fontsize=16)
ax1.set_xlabel('n', fontsize=16)
ax1.set_ylabel(y_axis_title, fontsize=18)
ax1.tick_params(axis='y', labelsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.7)
ax1.yaxis.set_major_formatter(FuncFormatter(
    lambda x, _: f'{int(round(x))}' if MODE == 'NFEV' else f'{round(x, 1)}'
))

plt.tight_layout()
os.makedirs(export_path, exist_ok=True)
plt.savefig(os.path.join(export_path, f"{prefix}chart.png"), dpi=300)
plt.show()
