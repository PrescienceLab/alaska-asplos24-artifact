import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re

f, axs = plt.subplots(2, figsize=(6, 3.5))
df = pd.read_csv('results/memcached-sweep.csv')


def errorbar(v):
  return (min(v), max(v))


###########################################

# g = sns.lineplot(data=df[df['name'] == 'alaska'],
#                  x='interval',
#                  y='AverageLatency(us)',
#                  hue='threads',
#                  palette='Set2',
#                  ax=axs[0]
# )

# g.set_ylabel('Latency (µs)')
# g.set_xlabel(None)
# g.grid(True, axis='y')


###########################################

g = sns.lineplot(data=df,
                 x='interval',
                 y='AverageLatency(us)',
                 hue='name',
                 palette='Set2',
                #  marker='o',
                 errorbar='sd',
                 ax=axs[0])


g.legend(ncol=2, fontsize='small')
g.set_ylabel('Latency (µs)\n(All thread counts)')
g.set_xlabel(None)

g.grid(True, axis='y')


###########################################
#             The bottom plot             #
###########################################

df = df.pivot_table(index=['threads', 'interval'],
                    columns=['name'],
                    # values='Throughput(ops/sec)',
                    values='AverageLatency(us)',
                    ).reset_index()

df['speedup'] = df['alaska'] / df['baseline']

g = sns.lineplot(data=df,
                 x='interval',
                 y='alaska',
                 hue='threads',
                 palette='Set2',
                #  marker='o',
                 ax=axs[1])
g.grid(True, axis='y')

g.set_ylabel('Avg. Latency (µs)\n(For each thread count)')
g.set_xlabel('Pause interval (milliseconds)')
g.legend(ncol=5, title='Thread count', fontsize='small')
plt.tight_layout()

plt.savefig('results/figure12.pdf', bbox_inches='tight', pad_inches=.05)
