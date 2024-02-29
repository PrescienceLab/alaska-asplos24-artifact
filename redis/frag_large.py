import time
import pandas as pd
import subprocess
from pathlib import Path
import os
# import numpy as np


if not 'ALASKA' in os.environ:
    print('ALASKA is not set.')
    exit()

ROOT_DIR = Path(os.path.dirname(__file__))
LOCAL = Path(os.environ['ALASKA']).resolve()
print(LOCAL)


def run_trials(binary, preload='', waiting_time=45 * 60, with_defrag=True, env={}, config='redis.conf'):
    environ = os.environ.copy()
    environ['LD_PRELOAD'] = str(LOCAL / 'lib' / 'librsstracker.so') + ' ' + preload
    environ['MALLOCSTATS'] = '2'

    if not with_defrag:
        environ['ANCH_NO_DEFRAG'] = '1'


    for k in env:
        environ[k] = str(env[k])

    environ['ANCH_AGGRO'] = '0.1'
    environ['FRAG_UB'] = '1.1'

    results = []
    print('starting...')
    os.system('rm -f dump.rdb rss.trace')

    # env['ALASKA_LOG'] = f'alaska_{trial}.log'
    redis_cmd = subprocess.Popen([binary, ROOT_DIR / config], env=environ, shell=False)
    time.sleep(.1) # Wait for the server to start

    os.system(f'cat {ROOT_DIR / "fragmentation-large.redis"} | redis/src/src/redis-cli')

    time.sleep(waiting_time)

    print('ending...')
    redis_cmd.kill()
    print('joining...')
    redis_cmd.wait()

    df = pd.read_csv('rss.trace', names=['time_ms', 'rss'])
    os.system('rm -f dump.rdb rss.trace')
    results.append(df)

    return pd.concat(results)


res = run_trials(ROOT_DIR / 'bin/redis-server-baseline', with_defrag=False)
res.to_csv('results/redis-baseline-large.csv', index=False)


res = run_trials(ROOT_DIR / 'bin/redis-server-alaska')
res.to_csv('results/redis-alaska-large.csv', index=False)



# MESH does not work w/ more than 64GB.
# libmesh = str(ROOT_DIR / 'mesh/bazel-bin/src/libmesh.so')
# res = run_trials(ROOT_DIR / 'bin/redis-server-baseline', preload=libmesh, with_defrag=False)
# res.to_csv('results/redis-mesh-large.csv', index=False)


res = run_trials(ROOT_DIR / 'bin/redis-server-ad', config='redis-ad.conf', with_defrag=False)
res.to_csv('results/redis-ad-large.csv', index=False)
