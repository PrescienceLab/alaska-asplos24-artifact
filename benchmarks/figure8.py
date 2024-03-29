# This script generates the new data required to plot figure 8.
# The baseline, and the alaska measurements are gathered when plotting figure 7.


import waterline as wl
import waterline.suites
import waterline.utils
import waterline.pipeline
import os
from pathlib import Path
from waterline.run import Runner
import pandas as pd

import seaborn as sns
import matplotlib as mpl
from matplotlib.lines import Line2D
from matplotlib import cm
import matplotlib.pyplot as plt

from .utils import find_spec, get_spec_size

# Construct the waterline workspace in the folder, `bench/`.
# This is where all benchmark sourcefiles and results will be saved.
space = wl.Workspace("bench")

# Grab alaska's linker flags using it's config tool.
linker_flags = os.popen("alaska-config --ldflags").read().strip().split("\n")

class AlaskaLinker(wl.Linker):
  command = "clang++"
  def link(self, ws, objects, output, args=[]):
    ws.shell("clang++", *args, '-ldl', *linker_flags, *objects, "-o", output)


class AlaskaStage(wl.pipeline.Stage):
  def __init__(self, extra_args = []):
    self.extra_args = extra_args

  def run(self, input, output, benchmark):
    aux_args = []
    env = os.environ.copy()
    if benchmark.suite.name == "SPEC2017":
      if benchmark.name == '602.gcc_s':
        # Handle GCC's funky garbage collector (Don't replace alloc_page)
        env['ALASKA_SPECIAL_CASE_GCC'] = 'true'
        print("Special case GCC allocator")

      if benchmark.name == '602.gcc_s' or benchmark.name == '600.perlbench_s':
        aux_args.append('--disable-hoisting')
        print("Disable hoisting!")
    
    space.shell(f"alaska-transform", *aux_args, *self.extra_args, input, '-o', output, env=env)



class OptStage(waterline.pipeline.Stage):
  def __init__(self, passes=[]):
    self.passes = passes

  def run(self, input, output, benchmark):
    space.shell('opt', *self.passes, input, '-o', output)


spec = find_spec()
if spec:
  print('Found spec here:', spec)
  space.add_suite(wl.suites.SPEC2017,
                  tar=spec,
                  # Disable perlbench and gcc
                  disabled=[600, 602],
                  config=get_spec_size())

space.clear_pipelines()



pl = waterline.pipeline.Pipeline("nohoisting")
pl.add_stage(OptStage(['-O3']), name="Optimize")
pl.add_stage(AlaskaStage(['--disable-hoisting']), name="Alaska")
pl.set_linker(AlaskaLinker())
space.add_pipeline(pl)


pl = waterline.pipeline.Pipeline("notracking")
pl.add_stage(OptStage(['-O3']), name="Optimize")
pl.add_stage(AlaskaStage(['--disable-tracking']), name="Alaska")
pl.set_linker(AlaskaLinker())
space.add_pipeline(pl)

res = space.run(runs=2, compile=True, run_name="figure8")
