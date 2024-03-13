import time
import pandas as pd
import subprocess
from pathlib import Path
import os
import numpy as np


if not 'ALASKA' in os.environ:
    print('ALASKA is not set.')
    exit()


MAX_GB = 50
INSERT_GB = MAX_GB * 2
GB_PER_STEP = INSERT_GB

OBJECT_SIZE = 500



ROOT_DIR = Path(os.path.dirname(__file__))
LOCAL = Path(os.environ['ALASKA']).resolve()


def run_trials(binary, preload='', waiting_time=10, with_defrag=True, env={}, config='redis.conf'):
    environ = os.environ.copy()
    if not with_defrag:
        environ['ANCH_NO_DEFRAG'] = '1'
    for k in env:
        environ[k] = str(env[k])

    # Set a constant upper bound
    environ['FRAG_UB'] = '1.1'

    environ['LD_PRELOAD'] = str(LOCAL / 'lib' / 'librsstracker.so') + ' ' + preload
    environ['MALLOCSTATS'] = '2'

    print(environ)

    results = []
    print('starting...')
    os.system('rm -f dump.rdb rss.trace')

    redis_cmd = subprocess.Popen([binary, ROOT_DIR / config], env=environ, shell=False)
    time.sleep(0.1) # Wait for the server to start

    os.system(f'cat {ROOT_DIR / "fragmentation-small.redis"} | redis/src/src/redis-cli > /dev/null')
    print('sleeping for', waiting_time)
    time.sleep(waiting_time)

    print('ending...')
    redis_cmd.kill()
    print('joining...')
    return_code = redis_cmd.wait()
    print(f'return code = {return_code}')

    df = pd.read_csv('rss.trace', names=['time_ms', 'rss'])
    os.system('rm -f dump.rdb rss.trace')
    results.append(df)

    print(results)

    return pd.concat(results)


os.makedirs('results/figure10/', exist_ok=True)

for lb in np.arange(1.0, 2, 0.5):
  for oh in np.arange(0.0, 0.25, 0.05):
    for aggro in np.arange(0.1, 1, 0.1):

        env = {
          'FRAG_LB': lb,
          'ANCH_AGGRO': aggro,
          'ANCH_TARG_OVERHEAD': oh
        }
        print(env)
        # continue
        res = run_trials(ROOT_DIR / 'bin/redis-server-alaska', env=env)
        res.to_csv(f'results/figure10/alaska-lb{lb}-oh{oh}-aggro{aggro}.csv', index=False)
