import os

def kill_processes(config_file):
    with open(config_file, 'r') as file:
        for line in file.readlines():
            host, port = line.strip().split()
            # 使用lsof命令找到在指定端口上运行的程序的PID
            command = f"lsof -t -i:{port}"
            pid = os.popen(command).read().strip()
            if pid:
                # 使用kill命令结束该程序
                os.system(f"kill -9 {pid}")

# 使用示例
kill_processes("../config/range-query-network.txt")