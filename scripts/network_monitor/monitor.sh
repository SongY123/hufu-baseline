#!/bin/bash

set -ex

sudo iptables -nvxt filter -L INPUT | grep $1 > record
sudo iptables -nvxt filter -L OUTPUT | grep $1 >> record

echo "Communication Cost: "
awk '{sum += $2};END {print sum}' record