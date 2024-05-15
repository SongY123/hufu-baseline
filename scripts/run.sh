#!/bin/bash
set -ex

spdz_path="dependency/MP-SPDZ"
log_path="../../output/logs"

cd $spdz_path

#program="knn"
#program="range_query"
#program="secret_union"
program="range_query_union"
#protocol="mascot"
protocol="shamir"
port=5001
./compile.py -E $protocol $program

silo=4
index=0
while ((index<silo))
do
  nohup ./$protocol-party.x -N $silo -p $index $program -OF $log_path/OUTPUT -h localhost -pn $port > $log_path/player$index.log &
  ((index++))
done

cd ../..