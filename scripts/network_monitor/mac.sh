#!/bin/bash

if [ ! -n "$1" ];then
  echo "Port cannot be empty!"
  echo "You can use the following command to monitor the port: bash monitor_traffic.sh 8888"
  exit
fi

export PORT=$1
echo "Monitoring port: "  ${PORT}

while true
do
  nettop -p tcp -J bytes_in,bytes_out -l 1 | grep :$PORT | awk '{print $3/1024, $4/1024}' >> record
  sleep 5
done