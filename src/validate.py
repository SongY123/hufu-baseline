def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        set1 = set(line.strip() for line in f1)
        set2 = set(line.strip() for line in f2)
    return set1 == set2

source_file = '../data/query/osm/osm_10_4/knn.csv'
target_file = '../data/query/osm/osm_10_4/predict_knn.csv'
# 比较knn.csv和predict_knn.csv
knn_result = compare_files(source_file, target_file)
print(f"{source_file} and {target_file} are \033[31m{'the same' if knn_result else 'different'}\033[0m")
