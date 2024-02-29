#!/usr/bin/env bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

buildstep() {
    NAME=$1
    shift
    "$@" 2>&1 | sed $'s|^|\x1b[90m['"${NAME}"$']\x1b[39m |' || exit 1
}

# Compile llvm, and gclang.
buildstep "pull toolchain" tools/build_deps.sh

source $ROOT/opt/enable-toolchain


mkdir -p build

for config in noservice anchorage; do
  mkdir -p build/alaska-${config}

  pushd build/alaska-${config} 2>/dev/null

    INSTALL_DIR=${ROOT}/opt/alaska-${config}

    buildstep "configure ${config}" \
      cmake $ROOT/alaska \
        -DCMAKE_INSTALL_PREFIX:PATH=${INSTALL_DIR} \
        -DALASKA_CONFIG=$ROOT/configs/config.${config}.cmake

    buildstep "build ${config}" make -j $(nproc) install

    # Create an enable file which can be sourced in bash
    ENABLE=$ROOT/opt/enable-alaska-${config}
    echo "source ${ROOT}/opt/enable-toolchain" > $ENABLE
    # Binary path
    echo "export PATH=$INSTALL_DIR/bin:\$PATH" >> $ENABLE
    # Library path
    echo "export LD_LIBRARY_PATH=$INSTALL_DIR/lib:\$LD_LIBRARY_PATH" >> $ENABLE
    # add a variable to tell where alaska is installed
    echo "export ALASKA=$INSTALL_DIR" >> $ENABLE
  popd 2>/dev/null
done
