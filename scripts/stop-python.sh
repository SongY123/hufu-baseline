#!/bin/bash

# 读取配置文件中的端口号
port=$(awk '{print $2}' ./config/range-query-network.txt)

# 查找使用这个端口的进程ID
pid=$(lsof -t -i:$port)

# 使用kill -9命令结束这个进程
if [ -n "$pid" ]; then
    kill -9 $pid
    echo "Killed process $pid on port $port"
else
    echo "No process running on port $port"
fi