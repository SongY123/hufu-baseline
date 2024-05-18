import os
import glob
import csv


def process_csv_files(input_path, output_path):
    # 获取输入路径下的所有csv文件
    csv_files = glob.glob(os.path.join(input_path, "*.csv"))

    # 遍历所有csv文件
    for i, csv_file in enumerate(csv_files):
        with open(csv_file, 'r') as infile:
            # 读取文件内容
            reader = csv.reader(infile)
            lines = [','.join(row).replace(',', ' ') for row in reader]

        # 写入到输出路径中的对应文件中
        with open(os.path.join(output_path, f"Input-P{i + 1}-0"), 'w') as outfile:
            outfile.write('\n'.join(lines))


# 使用示例
process_csv_files('/Users/songyang/Desktop/Project/Python/hufu-baseline/data/osm/osm_tiny',
                  '/Users/songyang/Desktop/Project/Python/hufu-baseline/dependency/MP-SPDZ/Player-Data')
