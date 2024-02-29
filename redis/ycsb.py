import time
import pandas as pd
import subprocess
from pathlib import Path
import os
import re
import pathlib


if not 'ALASKA' in os.environ:
    print('ALASKA is not set.')
    exit()


ROOT_DIR = Path(os.path.dirname(__file__))
ALASKA = Path(os.environ['ALASKA'])
LOCAL = (ALASKA / 'local').resolve()
print(LOCAL)

runNum = 0

def parse_ycsb_result(lines, name, workload):
  global runNum
  res = {}
  res['workload'] = workload
  res['name'] = name
  for l in lines:
    l.rstrip()

    # look for a match of pattern bin/ycsb
    if re.search('Command line:', l):
        # capture information for the next run
        runNum = runNum + 1
    elif re.search(r'^\[OVERALL\]'
                   r'|^\[SCAN\]'
                   r'|^\[INSERT\]'
                   r'|^\[UPDATE\]'
                   r'|^\[DELETE\]'
                   r'|^\[READ\]',
                   l):
      m = l.split(",")
      print(m)
      res[m[1].strip()] = [float(m[2].strip())]
  print(res)
  return pd.DataFrame.from_dict(res)


def ycsb(db, name, workload, opts = {}):
  option_string = ''
  for key in opts:
    option_string += f' -p {key}={str(opts[key])}'
  print(option_string)
  print('loading...')
  os.popen(f'{ROOT_DIR}/../ycsb/bin/ycsb load {db} -threads 10 -P {ROOT_DIR}/../ycsb/workloads/{workload} {option_string}').read()
  print('running...')
  res = os.popen(f'{ROOT_DIR}/../ycsb/bin/ycsb run {db} -threads 10 -P {ROOT_DIR}/../ycsb/workloads/{workload} {option_string}').read()
  return parse_ycsb_result(res.splitlines(), name, workload)


def run_workload(command, name, workload, trials=10, with_defrag=True, env={}):
    environ = os.environ.copy()
    # environ['LD_PRELOAD'] = str(LOCAL / 'lib' / 'librsstracker.so')
    if not with_defrag:
        environ['ANCH_NO_DEFRAG'] = '1'

    for k in env:
        environ[k] = str(env[k])

    results = []


    for _ in range(trials):
      print('starting...')

      os.system(f'killall {command[0]} 2>/dev/null')
      # env['ALASKA_LOG'] = f'alaska_{trial}.log'
      server_cmd = subprocess.Popen(command, env=environ, shell=False)
      time.sleep(.1) # Wait for the server to start


      res = ycsb('redis', name, workload, {
        'recordcount':    1000000,
        'operationcount': 1000000,
        'redis.host': '127.0.0.1',
        'redis.port': 6379,
      })

      server_cmd.kill()
      server_cmd.wait()
      results.append(res)

    return pd.concat(results)

    #   os.popen(f'{ROOT_DIR}/../ycsb/bin/ycsb load redis -P {ROOT_DIR}/../ycsb/workloads/{workload} -p redis.host=127.0.0.1 -p redis.port=6379 -p recordcount=1000000').read()
    #   res = os.popen(f'{ROOT_DIR}/../ycsb/bin/ycsb run redis -P {ROOT_DIR}/../ycsb/workloads/{workload} -p redis.host=127.0.0.1 -p redis.port=6379 -p recordcount=1000000').read()
    #   redis_cmd.kill()
    #   redis_cmd.wait()
    #   results.append(parse_ycsb_result(res.splitlines(), name, workload))
    #
    # return pd.concat(results)



outdir = pathlib.Path(f"{ROOT_DIR}/../results/ycsb/")
outdir.mkdir(parents=True, exist_ok=True)
results = []
for workload in "abcdef":
  res = run_workload([ROOT_DIR / 'bin/redis-server-alaska', ROOT_DIR / 'redis.conf'], 'alaska', 'workload' + workload, trials = 1)
  results.append(res)

  res = run_workload([ROOT_DIR / 'bin/redis-server-baseline', ROOT_DIR / 'redis.conf'], 'baseline', 'workload' + workload, trials = 1)
  results.append(res)
df = pd.concat(results)
df.to_csv(outdir / f'redis.csv', index=False)
