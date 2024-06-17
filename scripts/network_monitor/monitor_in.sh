#!/bin/bash

set -ex

iptables -nvt filter -L INPUT | grep $1
