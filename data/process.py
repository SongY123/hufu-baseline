import numpy as np

# 读取data_10w.txt文件
data = np.loadtxt('demo/data_10w.txt', skiprows=1)

# 处理longitude和latitude
data[:, 1:] = (data[:, 1:] + 101.0) / 10.0

# 保存到data_10w_new.txt文件
np.savetxt('demo/data_10w_new.txt', data, fmt=['%d', '%.2f', '%.2f'], delimiter=',')

# 读取query_10w.txt文件
query = np.loadtxt('demo/query_10w.txt', dtype={'names': ('query', 'val1', 'val2', 'val3'),
                                           'formats': ('S10', 'f4', 'f4', 'f4')}, skiprows=1)

# 处理第2、3个值
query['val1'] = (query['val1'] + 101.0) / 10.0
query['val2'] = (query['val2'] + 101.0) / 10.0

# 处理第4个值
query['val3'] = query['val3'] / 10.0

# 保存到query_10w_new.txt文件
with open('demo/query_10w_new.txt', 'w') as f:
    for (query, val1, val2, val3) in query:
        # 生成SQL语句
        sql = 'SELECT id FROM osm WHERE DWithin(Point(' + str(val1) + ',' + str(val2) + '), location,' + str(val3) + ');\n'
        print(sql)
        f.write(sql)