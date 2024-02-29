import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re


def format_memory_ticks_gb(value, _):
    # Convert kilobytes to megabytes
    value_in_gb = value / 1024 / 1024 / 1024
    return f'{value_in_gb:.0f} GB'

def format_seconds(ms, _):
    return f'{ms / 1000:.0f}s'

def format_minutes(ms, _):
    return f'{ms / 1000 / 60:.0f}m'

def format_percent(x, _):
    return f'{x * 100:.0f}%'


colors = {
    "alaska": "#0075ab",
    "nohoisting": "#aa6fc5",
    "notracking": "#ff6583",
    "noinlining": "#ffa600",
}

f, ax = plt.subplots(1, figsize=(5, 1.75), dpi=300)
# Read both of the csv files, filter them, and merge them
# we want four 'config' column values:
#   - baseline
#   - alaska
#   - notracking
#   - nohoisting
# And we only care about SPEC for this specific plot.

f7 = pd.read_csv('results/figure7.csv')
f7 = f7[f7['suite'] == 'SPEC2017']
# Remove GCC because we disable hoisting in it already.
f7 = f7[f7['benchmark'] != '602.gcc_s']
# Remove perlbench for the same reason
f7 = f7[f7['benchmark'] != '600.perlbench_s']

f8 = pd.read_csv('results/figure8.csv')

df = pd.concat([f7, f8])

df['key'] = df['suite'] + '@' + df['benchmark']



print(df['key'].unique())

baselines = df[df['config'] == 'baseline']
others = df[df['config'] != 'baseline']

metric = 'time'

dfs = []
for benchmark in baselines['key'].unique():
  print(benchmark)
  bl_filt = baselines[baselines['key'] == benchmark]
  mean = bl_filt[metric].mean()
  filt = pd.DataFrame(others[others['key'] == benchmark])
  filt['benchmark'] = benchmark.split('.')[1].split('_')[0]
  filt['overhead'] = (filt[metric] - mean) / mean
  dfs.append(filt)


df = pd.concat(dfs)

# df = df.sort_values(['benchmark'])
print(df)
g = sns.barplot(data=df,
            x='benchmark',
            y='overhead',
            hue='config',
            palette=colors,
            ci=None,
            linewidth=1,
            edgecolor='black',
            ax=ax)
g.set(xlabel=None, ylabel=None)

g.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, _: '{}%'.format(int(y * 100))))

# custom_y_ticks = list(map(lambda x: x / 100.0, range(0, 125, 25)))
# plt.yticks(custom_y_ticks, fontsize=8)
plt.legend(ncol=2, loc="upper right", fontsize=7, frameon=False)
plt.xticks(rotation=0, fontsize=7)
plt.grid(axis='y', linestyle='-', alpha=0.3, zorder=1)
plt.gca().set_axisbelow(True)
plt.tight_layout()

plt.savefig('results/figure8.pdf')
