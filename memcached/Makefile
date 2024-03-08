.DEFAULT_GOAL := redis
.PHONY: redis

src:
	git clone https://github.com/memcached/memcached.git src --recursive
	git -C src checkout 9723c0ea8ec1237b8364410ba982af8ea020a2b6

libevent:
	wget https://github.com/libevent/libevent/releases/download/release-2.1.12-stable/libevent-2.1.12-stable.tar.gz
	tar xvf libevent-2.1.12-stable.tar.gz
	mv libevent-2.1.12-stable libevent


MCD_FLAGS=CC=gclang 'CFLAGS=-O0 -gdwarf-4'
src/memcached: | src bin/libevent.bc
	cd src/ && ./autogen.sh ${MCD_FLAGS}
	cd src/ && ./configure ${MCD_FLAGS}
	cd src/ && make -j ${MCD_FLAGS}


bin/libevent.bc: | libevent
	@mkdir -p bin
	cd libevent/ && ./configure CC=gclang --disable-openssl
	cd libevent/ && make -j CC=gclang
	get-bc -b -o bin/libevent.bc libevent/.libs/libevent.so

bin/memcached.bc: src/memcached bin/libevent.bc
	@mkdir -p bin
	@echo " EX memcached"
	@get-bc -b -o bin/memcached-unlinked.bc src/memcached
	llvm-link bin/libevent.bc bin/memcached-unlinked.bc -o bin/memcached.bc
	@llvm-dis bin/memcached.bc



bin/memcached-alaska: bin/memcached.bc
	cp bin/memcached.bc bin/alaska.bc
	opt -O3 bin/alaska.bc -o bin/alaska.bc
	ALASKA_RELAX_VARARG=true alaska-transform bin/alaska.bc -o bin/alaska-transformed.bc
	llc -O3 bin/alaska-transformed.bc --relocation-model=pic --filetype=obj -o bin/alaska.o
	clang bin/alaska.o $(shell alaska-config --ldflags --cflags) -lm -ldl -o bin/memcached-alaska


bin/memcached-baseline: bin/memcached.bc
	cp bin/memcached.bc bin/baseline.bc
	opt -O3 bin/baseline.bc -o bin/baseline.bc
	ALASKA_RELAX_VARARG=true alaska-transform --baseline bin/baseline.bc -o bin/baseline-transformed.bc
	llc -O3 bin/baseline-transformed.bc --relocation-model=pic --filetype=obj -o bin/baseline.o
	clang bin/baseline.o $(shell alaska-config --cflags) -lm -ldl -o bin/memcached-baseline


memcached: bin/memcached-baseline bin/memcached-alaska

clean:
	rm -rf bin
	$(MAKE) -C clean


FORCE:
