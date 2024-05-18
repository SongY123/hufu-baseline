#!/bin/bash

set -ex

if [ ! -n "$1" ];then
  echo "Port cannot be empty!"
  echo "You can use the following command to restart the monitor: sudo bash restart.sh 8888"
  exit
fi

export PORT=$1
./stop.sh ${PORT}
./start.sh ${PORT}