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
LOCAL = Path(os.environ['ALASKA']).resolve()
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
      res[m[1].strip()] = [float(m[2].strip())]
  return pd.DataFrame.from_dict(res)



def ycsb(db, name, workload, opts = {}):
  option_string = ''
  for key in opts:
    option_string += f' -p {key}={str(opts[key])}'
  print(option_string)
  print('loading...')
  os.popen(f'{ROOT_DIR}/../ycsb/bin/ycsb load {db} -threads 1 -P {ROOT_DIR}/../ycsb/workloads/{workload} {option_string}').read()
  print('running...')
  res = os.popen(f'{ROOT_DIR}/../ycsb/bin/ycsb run {db} -threads 1 -P {ROOT_DIR}/../ycsb/workloads/{workload} {option_string}').read()
  df = parse_ycsb_result(res.splitlines(), name, workload)
  return df


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


      res = ycsb('memcached', name, workload, {
        'recordcount':    100000,
        'operationcount': 100000,
        'memcached.hosts': '127.0.0.1',
      })
      print('res = \n', res)

      server_cmd.kill()
      out = server_cmd.wait()
      print(f'exit code: {out}')
      results.append(res)

    return pd.concat(results)

results = []
for interval in range(50, 1100, 100):
  for threads in [1, 2, 4, 8, 16, 32]:
    print(interval, threads)
    for test in ['alaska', 'baseline']:
      env={
        'ANCH_MODE': 'stress',
        'STRESS_INTERVAL': str(interval),
        # 'STRESS_TOKENS': ??
      }

      print(env)
      res = run_workload([ROOT_DIR / f'bin/memcached-{test}', '-u', 'nobody', '-t', str(threads)],
                         test,
                         'workloada',
                         trials = 1,
                         env=env)
      res['threads'] = threads
      res['interval'] = interval
      print(res)
      results.append(res)

    # Save in-progress data
    outdir = pathlib.Path(f"{ROOT_DIR}/../results/")
    outdir.mkdir(parents=True, exist_ok=True)
    pd.concat(results).to_csv(outdir / f'memcached-sweep.csv', index=False)


