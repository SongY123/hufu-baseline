#!/bin/bash

set -ex

# 指定要清理的目录
base_dir="output"

# 遍历目录下的所有子目录
for dir in "$base_dir"/*; do
    # 确保这是一个目录，而不是文件
    if [ -d "$dir" ]; then
        # 遍历目录下的所有文件
        for file in "$dir"/*; do
            # 确保这是一个文件，而不是目录
            if [ -f "$file" ]; then
                # 删除文件
                rm "$file"
            fi
        done
    fi
done