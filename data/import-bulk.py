import psycopg2
import os
import time

# 定义数据库连接参数
host = 'localhost'
port = '54321'
username = 'hufu'
password = 'hufu'
dbname = 'osm_db'
base_path = './'
input_path = base_path + 'osm/osm_10_4'
output_path = base_path + 'query/knn/osm_10_4'
if_clean = True
prefix = 'osm'

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

# 创建一个新的游标
cur = conn.cursor()

# 获取input_path下的所有文件
files = os.listdir(input_path)

tables = []

for file in files:
    suffix = os.path.splitext(file)[0].split('_')[-1]
    tables.append(f"{prefix}_{suffix}")

if if_clean:
    drop_view_sql = f"DROP VIEW IF EXISTS {prefix}"
    cur.execute(drop_view_sql)
    for table in tables:
        # 检查表是否存在，如果存在则删除
        drop_table_sql = f"DROP TABLE IF EXISTS {table}"
        print(f"Executing SQL: {drop_table_sql}")
        cur.execute(drop_table_sql)

    # 提交事务
    conn.commit()

for file in files:
    # 获取文件的后缀名
    suffix = os.path.splitext(file)[0].split('_')[-1]

    # 创建一个临时表
    start_time = time.time()
    print("Creating temp_table...")
    cur.execute('''
    CREATE TEMP TABLE temp_table (
        id INT8,
        longitude FLOAT,
        latitude FLOAT
    )
    ''')
    print(f"Temp table created. Time taken: %.3f seconds" % (time.time() - start_time))

    # 使用COPY命令将数据从CSV文件导入到临时表中
    start_time = time.time()
    print(f"Importing data from {file} to temp_table...")
    with open(os.path.join(input_path, file), 'r') as f:
        cur.copy_from(f, 'temp_table', sep=',')
    print(f"Data imported to temp_table. Time taken: %.3f seconds" % (time.time() - start_time))

    # 从临时表中选择数据并将其插入到目标表中
    start_time = time.time()
    print(f"Importing data from temp_table to {prefix}_{suffix}...")
    cur.execute(f'''
    CREATE TABLE {prefix}_{suffix} AS
    SELECT id AS id , ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS location
    FROM temp_table
    ''')
    print(f"Data imported to {prefix}_{suffix}. Time taken: %.3f seconds" % (time.time() - start_time))

    # 提交事务
    conn.commit()

    # 删除临时表
    start_time = time.time()
    print("Dropping temp_table...")
    cur.execute('DROP TABLE temp_table')
    print(f"Temp table dropped. Time taken: %.3f seconds" % (time.time() - start_time))

view_sql = "CREATE VIEW " + prefix + " AS " + " UNION ALL ".join([f"SELECT * FROM {table}" for table in tables])
print(f"Creating view with SQL: {view_sql}")
cur.execute(view_sql)
conn.commit()

# 关闭游标和连接
cur.close()
conn.close()