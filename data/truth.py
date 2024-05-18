import time

import psycopg2
import csv
import os

# 定义数据库连接参数
host = "localhost"
port = "54321"
username = "hufu"
password = "hufu"
dbname = "osm_db"
output_path = "./query/osm/osm_10_7"

# 连接到数据库
conn = psycopg2.connect(
    host=host,
    port=port,
    user=username,
    password=password,
    dbname=dbname
)

# 创建一个新的游标
cur = conn.cursor()


global_view = "osm"
# 定义查询类型和对应的SQL语句
queries = {
    "range_query": f"SELECT id FROM {global_view} WHERE location <-> ST_GeomFromText('POINT(114 22)', 4326) < 1",
    "range_counting": f"SELECT COUNT(*) cnt FROM {global_view} WHERE location <-> ST_GeomFromText('POINT(114 22)', 4326) < 1",
    "knn": f"SELECT id FROM {global_view} ORDER BY location <-> ST_GeomFromText('POINT(114 22)', 4326) ASC LIMIT 5;"
}

if not os.path.exists(output_path):
    os.makedirs(output_path)

# 对每种查询类型执行查询并将结果输出到文件
for query_type, query_sql in queries.items():
    start_time = time.time()
    print(f"Executing SQL: {query_sql}")
    cur.execute(query_sql)
    results = cur.fetchall()
    end_time = time.time()  # 获取结束时间
    print(f"Execution time: %.3f seconds" % (end_time - start_time))  # 打印执行时间，保留3位小数

    with open(f"{output_path}/{query_type}.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(results)

# 关闭游标和连接
cur.close()
conn.close()