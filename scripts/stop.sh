#!/bin/bash
set -ex

#protocol="mascot"
protocol="shamir"
ps -ef | grep $protocol | grep -v  grep |awk '{print "kill -9 "$2}'|bash