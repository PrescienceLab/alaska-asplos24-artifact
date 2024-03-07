import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
import pandas
import matplotlib.ticker as tkr  
import numpy as np
import sys
from matplotlib.patches import Patch
import glob



fig, axs = plt.subplots(1, 1, figsize=(6,2))
plt.style.use("bmh")
# plt.figure(figsize=(6,3))
# plt.figure().set_figwidth(15)



colors = [
    "#0075ab",
    "#aa6fc5",
    "#ff6583",
    "#ffa600",
]
def sizeof_fmt(x, pos):
    return '%3.0f' % (x / 1024.0 / 1024.0)

def time_ms_fmt(x, pos):
    return '%d' % (x // 1000)

all = []
def load_and_plot(csv, color, **kwargs):
    df = pandas.read_csv(csv)

    scale = 50
    df['time_ms'] = (df['time_ms'].astype('int') // scale) * scale

    if np.max(df['time_ms']) < 9000:
        return

    mean = df.groupby('time_ms')['rss'].mean()
    std = df.groupby('time_ms')['rss'].std()
    std = std.fillna(0.0)

    x = mean.index.to_numpy(dtype=int)
    time_ms = mean.values

    def make_line_ci(axes, y, low, high, alpha):
        for x_val, y_val, l, h in zip(x, y, low, high):
            axes.vlines(x=x_val, ymin=l, ymax=h, color=color, alpha=alpha, linewidth=4)

    def upper(sigma_coeff):
        return mean - sigma_coeff * std

    def lower(sigma_coeff):
        return mean + sigma_coeff * std

    axs.plot(x, time_ms, color=color, **kwargs, zorder=3)
    all.append(df)


axs.axhline(y=100 * 1024 * 1024, linestyle="-", linewidth=1, color="#000000")




color = iter(colors)
c = next(color)
c_alaska = c

for csv in glob.glob('results/figure10/alaska-*.csv'):
    load_and_plot(csv, c, linewidth=2, alpha=0.2)


all_df = pandas.concat(all)

mins = all_df.groupby('time_ms')['rss'].min()
maxs = all_df.groupby('time_ms')['rss'].max()
mean = all_df.groupby('time_ms')['rss'].mean()
x = mean.index.to_numpy(dtype=int)

c = '#54EE2E'
c = next(color)
c = next(color)
c = next(color)
c_control = c
axs.plot(x, mins, "--", color=c, zorder=4, alpha=1)
axs.plot(x, maxs, "--", color=c, zorder=4, alpha=1)
axs.fill_between(x, mins, maxs, interpolate=True, color=c, alpha=0.1, zorder=1) 


MB = 1024 * 1024
major_ticks = np.arange(0, 350 * MB, 50 * MB)
# minor_ticks = np.arange(0, 350 * 1024 * 1024, 10 * 1024 * 1024)

axs.set_yticks(major_ticks)
# axs.set_yticks(minor_ticks, minor=True)
axs.grid(which='minor', alpha=0.2)
axs.grid(which='major', alpha=0.5)


axs.grid(True)
axs.legend(loc='lower right', ncol=3)

legend_elements = [
    Patch(facecolor=c_alaska, edgecolor='black', label='Anchorage Configurations'),
    Patch(facecolor=c_control, edgecolor='black', label='Envelope of Control'),
]
axs.legend(handles=legend_elements, facecolor='white', framealpha=1, fontsize=9.5)

axs.set_ylim(bottom=0.0)
axs.set_xlim(left=0.0, right=10000)
# axs.set_xlim(left=0.0, right=6000)
axs.yaxis.set_major_formatter(tkr.FuncFormatter(sizeof_fmt))
axs.xaxis.set_major_formatter(tkr.FuncFormatter(time_ms_fmt))

axs.set(xlabel='Time (s)',
        ylabel='RSS (MB)')

plt.tight_layout()
plt.savefig('results/figure10.pdf', bbox_inches='tight', pad_inches=.05)
