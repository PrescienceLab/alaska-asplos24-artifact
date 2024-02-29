#!/bin/bash

# Find the root of the artifact
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/../"

mkdir -p $ROOT/opt
pushd $ROOT/opt


touch $ROOT/opt/enable-toolchain



LLVM_VERSION=15.0.2

PREFIX_LLVM=$(realpath "$ROOT/opt/llvm")
PREFIX_GLLVM=$(realpath "$ROOT/opt/gllvm")



rm -f $ROOT/opt/enable-toolchain
echo "export PATH=$PREFIX_LLVM/bin:\$PATH" >> $ROOT/opt/enable-toolchain
echo "export LD_LIBRARY_PATH=$PREFIX_LLVM/lib:\$LD_LIBRARY_PATH" >> $ROOT/opt/enable-toolchain


echo "export PATH=$PREFIX_GLLVM/bin:\$PATH" >> $ROOT/opt/enable-toolchain
echo "export LD_LIBRARY_PATH=$PREFIX_GLLVM/lib:\$LD_LIBRARY_PATH" >> $ROOT/opt/enable-toolchain




if [ ! -f ${PREFIX_GLLVM}/bin/gclang ]; then

	mkdir -p ${PREFIX_GLLVM}
	# install go
	KERNEL=$(uname | tr '[:upper:]' '[:lower:]')

	case $(uname -p) in
		x86_64)
			ARCH=amd64
			;;
		arm)
			ARCH=arm64
			;;
		aarch64)
			ARCH=arm64
			;;
	esac

	wget -O go.tar.gz https://golang.google.cn/dl/go1.19.1.${KERNEL}-${ARCH}.tar.gz
	tar xvf go.tar.gz

	GOPATH=${PREFIX_GLLVM} GO111MODULE=off ${ROOT}/opt/go/bin/go get -v github.com/SRI-CSL/gllvm/cmd/...

fi




if [ ! -f "${PREFIX_LLVM}/bin/clang" ]; then
	mkdir -p ${PREFIX_LLVM}

	LLVM_FILE=""

	if [ "$(uname)" == "Linux" ]; then
		case $(uname -m) in
			x86_64)
				# the RHEL version is more stable on other distributions, it seems
				LLVM_FILE=clang+llvm-15.0.2-x86_64-unknown-linux-gnu-rhel86.tar.xz
				# LLVM_FILE=clang+llvm-16.0.3-x86_64-linux-gnu-ubuntu-22.04.tar.xz
				;;
			arm)
				LLVM_FILE=clang+llvm-15.0.2-aarch64-linux-gnu.tar.xz
				# LLVM_FILE=clang+llvm-16.0.3-aarch64-linux-gnu.tar.xz
				;;
			aarch64)
				LLVM_FILE=clang+llvm-15.0.2-aarch64-linux-gnu.tar.xz
				# LLVM_FILE=clang+llvm-16.0.3-aarch64-linux-gnu.tar.xz
				;;
		esac
	fi


	if [ "$(uname)" == "Darwin" ]; then
		case $(uname -m) in
			arm64)
		LLVM_FILE=clang+llvm-15.0.2-arm64-apple-darwin21.0.tar.xz
				;;
		esac
	fi

	# LLVM_FILE=""

	if [ "${LLVM_FILE}" != "" ]; then

		if [ ! -f llvm.tar.xz ]; then
			wget -O llvm.tar.xz https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVM_VERSION}/$LLVM_FILE
		fi
		tar xvf llvm.tar.xz --strip-components=1 -C ${PREFIX_LLVM}

	else
		echo "We have to compile LLVM from source on your platform..."
		sleep 4
		if [ ! -d llvm-project-${LLVM_VERSION}.src ]; then
			wget -O llvm.tar.xz https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVM_VERSION}/llvm-project-${LLVM_VERSION}.src.tar.xz
			tar xvf llvm.tar.xz
		fi
		pushd llvm-project-${LLVM_VERSION}.src
			mkdir -p build
			pushd build
				cmake ../llvm -G Ninja                                    \
					-DCMAKE_INSTALL_PREFIX=${PREFIX_LLVM}                        \
					-DCMAKE_BUILD_TYPE=Release                              \
					-DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra;openmp;compiler-rt" \
					-DLLVM_TARGETS_TO_BUILD="X86;AArch64;RISCV"
					# -DLLVM_ENABLE_LLD=True

				ninja install
			popd
		popd
	fi

	# rm -rf llvm.tar.xz

	

fi
