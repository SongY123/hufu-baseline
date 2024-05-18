#!/bin/bash

set -ex

if [[ "$OSTYPE" == "darwin"* ]]; then
  sudo pfctl -s info > record
else
  iptables -nvxt filter -L INPUT | head -n 12 | tail -n 10 > record
  iptables -nvxt filter -L OUTPUT | head -n 12 | tail -n 10 >> record
fi

echo "Communication Cost: "
awk '{sum += $2};END {print sum}' record