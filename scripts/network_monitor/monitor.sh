#!/bin/bash

set -ex

sudo iptables -nvxt filter -L INPUT > record
sudo iptables -nvxt filter -L OUTPUT >> record

echo "Communication Cost: "
awk '{sum += $2};END {print sum}' record