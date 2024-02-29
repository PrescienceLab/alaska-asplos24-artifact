(use-modules (guix)
             (guix packages)
             (gnu packages)
             (gnu packages certs)
             (gnu packages wget)
             (gnu packages version-control)
             (gnu packages libunwind)
             (gnu packages moreutils)
             (gnu packages python)
             (gnu packages python-xyz)
             (gnu packages bash)
             (gnu packages commencement)
             (gnu packages compression)
             (gnu packages gcc)
             (gnu packages llvm)
             (gnu packages cmake)
             (gnu packages build-tools)
             (gnu packages base)
             (gnu packages gawk)
             (gnu packages file)
             (gnu packages ncurses)
             (gnu packages pkg-config)
             (gnu packages linux))

(packages->manifest
 (list gcc
       gcc-toolchain
       ;; This gives us libstdc++ & libgcc_s
       ;; Those should be in gcc-toolchain, in my opinion
       (list gcc "lib")
       nss-certs wget
       git
       zlib
       libunwind
       cmake
       gnu-make
       coreutils moreutils binutils util-linux
       findutils
       ;; Some scripts expect to have various locale environment variables set
       ;; For example, LC_COLLATE=en_US
       glibc-locales
       ;; For submission scripts
       tar gzip bzip2 xz
       ;; For grading scripts
       ncurses sed diffutils gawk grep
       ;; Data Collection & Plotting
       python
       python-virtualenv
       file
       which
       pkg-config
       ;; General scripting
       bash))

;; export CPLUS_INCLUDE_PATH="$GUIX_ENVIRONMENT/include/c++/x86_64-unknown-linux-gnu${CPLUS_INCLUDE_PATH:+:}$CPLUS_INCLUDE_PATH"
;; export LD_LIBRARY_PATH="$GUIX_ENVIRONMENT/lib${LD_LIBRARY_PATH:+:}$LD_LIBRARY_PATH"

;; guix shell -m manifest.scm --container -N --emulate-fhs
