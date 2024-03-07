
# Tell the makefile to use bash instead of sh
SHELL := /usr/bin/env bash

all:
	@echo "Read README.md"

venv: venv/touchfile
venv/touchfile: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile



results/figure7.csv: venv
	@echo "Generating data for figure 7"
	@. venv/bin/activate \
	   && . opt/enable-alaska-noservice \
		 && ulimit -s unlimited \
		 && python3 -m benchmarks.figure7
	mkdir -p results
	cp bench/results/figure7/all.csv results/figure7.csv


results/figure7.pdf: venv results/figure7.csv
	@echo "Generating figure 7"
	@mkdir -p results
	@. venv/bin/activate \
		&& python3 plotgen/figure7.py




# Figure8 is a superset of figure 7, so we generate partial data then
# merge them in the plotting script.
# It wouldn't make sense to re-run spec's baseline.
results/figure8.csv: venv
	@echo "Generating data for figure 8"
	@. venv/bin/activate \
	   && . opt/enable-alaska-noservice \
		 && ulimit -s unlimited \
		 && python3 -m benchmarks.figure8
	cp bench/results/figure8/all.csv results/figure8.csv


results/figure8.pdf: venv results/figure8.csv | results/figure7.csv
	@echo "Generating figure 8"
	@mkdir -p results
	@. venv/bin/activate \
		&& python3 plotgen/figure8.py






# Build memcached w/ anchorage
memcached/bin/memcached-alaska:
	@ . opt/enable-alaska-anchorage \
		&& $(MAKE) -C memcached memcached

# Build redis w/ anchorage
redis/bin/redis-server-alaska: venv opt/enable-alaska-anchorage
	@. venv/bin/activate && \
		. opt/enable-alaska-anchorage \
		&& $(MAKE) -C redis redis

redis/bin/redis-server-ad: venv opt/enable-alaska-anchorage
	@. venv/bin/activate && \
		. opt/enable-alaska-anchorage \
		&& $(MAKE) -C redis redis




# Create the results for redis
results/figure9.pdf: venv

	@echo "Compiling redis"
	@. opt/enable-alaska-anchorage \
		&& make -C redis redis

	@echo "Generating data for figure 9"
	@mkdir -p results
	@. venv/bin/activate \
		&& . opt/enable-alaska-anchorage \
		&& ulimit -s unlimited \
		&& python3 -m redis.frag \
		&& python3 plotgen/figure9.py




results/figure10.pdf: venv | results/figure9.pdf
	@echo "Generating data for figure 9"
	@mkdir -p results
	@. venv/bin/activate \
		&& . opt/enable-alaska-anchorage \
		&& ulimit -s unlimited \
		&& python3 -m redis.config_sweep \
		&& python3 plotgen/figure10.py



# Create the results for redis (the large version)
results/redis-alaska-large.csv: venv redis/bin/redis-server-alaska
	@echo "Generating data for figure 11"
	@mkdir -p results
	@. venv/bin/activate \
	   && . opt/enable-alaska-anchorage \
		 && ulimit -s unlimited \
		 && python3 -m redis.frag_large

results/figure11.pdf: venv results/redis-alaska-large.csv
	@echo "Plotting figure 11"
	@. venv/bin/activate \
		&& python3 plotgen/figure9.py




results/memcached-sweep.csv: venv memcached/bin/memcached-alaska
	@echo "Generating data for figure 9"
	@mkdir -p results
	@. venv/bin/activate \
	   && . opt/enable-alaska-anchorage \
		 && ulimit -s unlimited \
		 && python3 -m memcached.ycsb

results/figure12.pdf: venv results/memcached-sweep.csv
	@echo "Plotting figure 12"
	@. venv/bin/activate \
		&& python3 plotgen/figure12.py



compile:
	@./build.sh



distclean:
	make -C redis clean
	rm -rf opt build bench

# If these files don't exist, we need to compile.
opt/enable-alaska-noservice: compile
opt/enable-alaska-anchorage: compile

in-docker: FORCE
	docker build -t alaska-asplos24ae .
	# 
	# docker run -it --rm --mount type=bind,source=${PWD},target=/artifact alaska-asplos24ae
	docker run -it --cpus 0.5 --rm --volume ${PWD}:/artifact:z alaska-asplos24ae

FORCE:
