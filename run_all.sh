#!/usr/bin/env bash


buildstep() {
  NAME=$1
  shift
  printf "\e[32m${NAME}\e[0m\n"
  # "$@" 2>&1 | sed $'s|^|\x1b[32m['"${NAME}"$']\x1b[39m |' || exit 1
  "$@"
}

confirm_continue() {
  read -p "$1 (y/N) " answer

  if [[ $answer =~ ^[Yy]$ ]]; then
    echo "Continuing"
  else
    # User declined, exit or perform alternative action
    echo "Exiting..."
    exit 1
  fi
}

if [ -z "$TMUX" ]; then
  # $TMUX is empty or not defined
  echo "We have detected you are not running in a tmux session. This is highly recommended,"
  echo "as running the entire artifact could take a day or more, if SPEC is enabled."
  echo "Note: This may be a false positive if you are in a docker container"
  confirm_continue "Are you sure you want to continue without TMUX?"
fi



spec_location=""

for location in ./ ~ /; do
  if [[ -f "$location/SPEC2017.tar.gz" ]]; then
    spec_location=$(realpath "$location/SPEC2017.tar.gz")
    break
  fi
done

if [[ "$spec_location" == "" ]]; then
  printf "\e[31m"
  echo "We didn't find a SPEC install in any of these locations: /SPEC2017.tar.gz, ./SPEC2017.tar.gz, or ~/SPEC2017.tar.gz."
  echo "The artifact will work correctly but figure 7 will not contain SPEC, and figure 8 will not be generated."
  printf "\e[0m"
  confirm_continue "Would you like to continue?"
else
  echo "Found SPEC here: $spec_location"
fi



memory=$(free -h | grep Mem | awk '{print $7}')
generate_figure11=false
read -p "Would you like to generate figure 11? It requires upwards of 200GiB of memory. You have ${memory}B free now. (y/N) " answer
if [[ $answer =~ ^[Yy]$ ]]; then
  generate_figure11=true
fi
echo $generate_figure11





echo "Setting up virtual environment"
make venv

buildstep "compile" ./build.sh

buildstep "Figure 7" make results/figure7.pdf

if [[ "$spec_location" != "" ]]; then
  buildstep "Figure 8" make results/figure8.pdf
else
  echo "Skipping figure 8, because SPEC is not found"
fi

buildstep "Figure 9" make results/figure9.pdf

buildstep "Figure 10" make results/figure10.pdf

if [[ "$generate_figure11" == "true" ]]; then
  buildstep "Figure 11" make results/figure11.pdf
else
  echo "Skipping Figure 11"
fi

buildstep "Figure 12" make results/figure12.pdf
