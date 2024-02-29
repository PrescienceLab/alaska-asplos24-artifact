import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
import pandas
import matplotlib.ticker as tkr  
import numpy as np
import sys


# mesh = pandas.read_csv('data/redis/mesh2y-raw.tsv', sep='\t')
# mesh['time_ms'] = (mesh['time'] / 1000 / 1000)
# mesh.to_csv('data/redis/mesh.csv', index=False)
#
#
# mesh = pandas.read_csv('data/redis/jemalloc-raw.tsv', sep='\t')
# mesh['time_ms'] = (mesh['time'] / 1000 / 1000)
# mesh.to_csv('data/redis/jemalloc.csv', index=False)
# print(mesh)
#
fig, axs = plt.subplots(1, 1, figsize=(6,2))
# plt.style.use("bmh")
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

def load_and_plot(csv, label, color, **kwargs):
    df = pandas.read_csv(csv)

    scale = 100
    df['time_ms'] = (df['time_ms'].astype('int') // scale) * scale

    mean = df.groupby('time_ms')['rss'].mean()
    std = df.groupby('time_ms')['rss'].std()
    std = std.fillna(0.0)
    mins = df.groupby('time_ms')['rss'].min()
    maxs = df.groupby('time_ms')['rss'].max()

    x = mean.index.to_numpy(dtype=int)
    time_ms = mean.values

    def make_line_ci(axes, y, low, high, alpha):
        for x_val, y_val, l, h in zip(x, y, low, high):
            axes.vlines(x=x_val, ymin=l, ymax=h, color=color, alpha=alpha, linewidth=4)

    def upper(sigma_coeff):
        return mean - sigma_coeff * std

    def lower(sigma_coeff):
        return mean + sigma_coeff * std

    axs.plot(x, time_ms, label=label, color=color, **kwargs)
    # axs.plot(x, mins, "-", label=label, color=color)
    # axs.plot(x, maxs, "-", label=label, color=color)

    # axs.fill_between(x, lower(1), upper(1), interpolate=False, color=color, alpha=0.20)
    # axs.fill_between(x, lower(2), upper(2), interpolate=True, color=color, alpha=0.15)
    # axs.fill_between(x, lower(3), upper(3), interpolate=True, color=color, alpha=0.05)
    # make_line_ci(axs, time_ms, time_ms - 1*std, time_ms + 1*std, alpha=0.15)
    # make_line_ci(axs, time_ms, time_ms - 2*std, time_ms + 2*std, alpha=0.10)
    # make_line_ci(axs, time_ms, time_ms - 3*std, time_ms + 3*std, alpha=0.05)

    # axs.fill_between(x, mins, maxs, interpolate=True, color=color, alpha=0.4) 


axs.axhline(y=100 * 1024 * 1024, linestyle="-", linewidth=1, color="#000000")




color = iter(colors)

c = next(color)
load_and_plot('results/redis-alaska.csv', 'Anchorage', c, linewidth=3)
# c = next(color)
# load_and_plot('nodefrag.csv', 'Anchorage (No defrag)', c)
c = next(color)
load_and_plot('results/redis-baseline.csv', 'Baseline', c, linestyle='--')

c = next(color)
load_and_plot('results/redis-mesh.csv', 'Mesh', c, linestyle=':')
c = next(color)
load_and_plot('results/redis-ad.csv', 'activedefrag', c, linestyle='--')


MB = 1024 * 1024
major_ticks = np.arange(0, 350 * MB, 50 * MB)
# minor_ticks = np.arange(0, 350 * 1024 * 1024, 10 * 1024 * 1024)

axs.set_yticks(major_ticks)
# axs.set_yticks(minor_ticks, minor=True)
axs.grid(which='minor', alpha=0.2)
axs.grid(which='major', alpha=0.5)


axs.grid(True)
# axs.legend(loc='lower right', ncol=3)
axs.legend(loc='lower right', ncol=4, facecolor='white', framealpha=1, fontsize=9.5)

axs.set_ylim(bottom=0.0)
axs.set_xlim(left=0.0, right=10000)
# axs.set_xlim(left=0.0, right=6000)
axs.yaxis.set_major_formatter(tkr.FuncFormatter(sizeof_fmt))
axs.xaxis.set_major_formatter(tkr.FuncFormatter(time_ms_fmt))

axs.set(xlabel='Time (s)',
        ylabel='RSS (MB)')

# plt.tight_layout()
plt.savefig('results/figure9.pdf', bbox_inches='tight', pad_inches=.05)
