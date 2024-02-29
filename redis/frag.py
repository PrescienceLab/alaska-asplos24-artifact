import time
import pandas as pd
import subprocess
from pathlib import Path
import os
# import numpy as np


if not 'ALASKA' in os.environ:
    print('ALASKA is not set.')
    exit()


MAX_GB = 50
INSERT_GB = MAX_GB * 2
GB_PER_STEP = INSERT_GB

OBJECT_SIZE = 500



ROOT_DIR = Path(os.path.dirname(__file__))
LOCAL = Path(os.environ['ALASKA']).resolve()


def run_trials(binary, preload='', waiting_time=30 * 60, with_defrag=True, env={}, config='redis.conf'):
    environ = os.environ.copy()
    if not with_defrag:
        environ['ANCH_NO_DEFRAG'] = '1'
    for k in env:
        environ[k] = str(env[k])
    environ['ANCH_AGGRO'] = '0.1'
    environ['FRAG_UB'] = '1.1'


    environ['LD_PRELOAD'] = str(LOCAL / 'lib' / 'librsstracker.so') + ' ' + preload
    environ['MALLOCSTATS'] = '2'

    results = []
    print('starting...')
    os.system('rm -f dump.rdb rss.trace')

    redis_cmd = subprocess.Popen([binary, ROOT_DIR / config], env=environ, shell=False)
    time.sleep(.1) # Wait for the server to start

    os.system(f'cat {ROOT_DIR / "fragmentation-small.redis"} | redis/src/src/redis-cli')
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





res = run_trials('redis/bin/redis-server-ad',
                 config='redis-ad.conf',
                 waiting_time = 10)
res.to_csv('results/redis-ad.csv', index=False)

res = run_trials('redis/bin/redis-server-baseline',
                 waiting_time=10)
res.to_csv('results/redis-baseline.csv', index=False)


res = run_trials('redis/bin/redis-server-alaska',
                 waiting_time=10)
res.to_csv('results/redis-alaska.csv', index=False)


libmesh = str(ROOT_DIR / 'mesh/bazel-bin/src/libmesh.so')
res = run_trials(ROOT_DIR / 'bin/redis-server-baseline',
                 waiting_time=10,
                 preload=libmesh)
res.to_csv('results/redis-mesh.csv', index=False)

# res = run_trials(ROOT_DIR / 'bin/redis-server-alaska', waiting_time=45 * 60) # 20 minutes
# res.to_csv('anchorage.csv', index=False)

# res = run_trials(ROOT_DIR / 'bin/redis-server-baseline', waiting_time=45 * 60)
# res.to_csv('baseline.csv', index=False)
