#!/bin/bash

set -ex

iptables -nvt filter -L OUTPUT | grep $1
