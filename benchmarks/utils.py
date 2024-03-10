import os

from pathlib import Path

def get_spec_size():
  size = os.getenv("SPEC_SIZE")

  if size:
    if size in ['test', 'train', 'ref']:
      return size
    else:
      print(f'{size} is not one of test,train,ref')

  print("Using SPEC size 'ref'")
  return 'ref'

spec_locations = [
    "./SPEC2017.tar.gz",
    "~/SPEC2017.tar.gz",
    "/SPEC2017.tar.gz",
]
def find_spec():
    print('looking for SPEC in these locations:', spec_locations)
    for loc in spec_locations:
        loc = os.path.expanduser(loc)
        if os.path.isfile(loc):
            return str(Path(loc).resolve())
    return None
