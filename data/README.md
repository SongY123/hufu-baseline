# 运行说明
项目依赖Python3.7和PostGIS数据库。请确保你的系统中已经安装了Python3和PostGIS数据库。

## 使用docker启动PostGIS
你可以使用Docker命令来拉取`kartoza/postgis`的镜像并启动。以下是具体的步骤：

1. 拉取镜像：使用`docker pull`命令来拉取`kartoza/postgis`的镜像。这个命令的格式是`docker pull <image_name>`，其中`<image_name>`是你要拉取的镜像的名称。

```bash
docker pull kartoza/postgis
```

2. 启动容器：使用`docker run`命令来启动一个`kartoza/postgis`的容器。这个命令的格式是`docker run [options] <image_name>`，其中`<image_name>`是你要启动的容器的镜像的名称，`[options]`是一些可选的参数，例如：

- `-d`: 这个参数表示在后台运行容器，并返回容器ID。
- `-p`: 这个参数用来设置容器的端口映射，格式是`-p <host_port>:<container_port>`，其中`<host_port>`是主机的端口，`<container_port>`是容器的端口。
- `--name`: 这个参数用来设置容器的名称。

例如，以下命令会启动一个`kartoza/postgis`的容器，容器的名称是`postgis`，用户名是`hufu`，密码是`hufu`，将主机的`/docker_root/postgresql11-docker`目录映射到容器的`/var/lib/postgresql`以持久化数据，并将容器的5432端口映射到主机的54321端口：

```bash
$ docker run -d --name postgis --restart always -e POSTGRES_USER=hufu -e POSTGRES_PASS='hufu' -e ALLOW_IP_RANGE=0.0.0.0/0 -v /docker_root/postgresql11-docker:/var/lib/postgresql -p 54321:5432 -t kartoza/postgis
```

# 数据文件夹结构

`data`文件夹是用来存储和组织所有相关数据的地方。以下是`data`文件夹的主要结构和内容：

- `osm`: 这个文件夹包含了OpenStreetMap的数据。文件夹的命名规则是“osm_10_x”，其中数据默认划分为6方，数据集数量为$10^x$。

- `traffic`: 这个文件夹包含了北京出租车的数据。文件夹的命名规则是"traffic_x"，其中数据划分为x方，数据总量不变。

- `query`: 这个文件夹包含了各种查询的示例。每种查询类型下的文件夹为对应数据集的查询结果。

每行数据的格式为id,longtitude,latitude，其中id为long，longtitude和latitude为float，有效位数为小数点后7位。对于osm数据集来说，id的表示范围超过int(32位)的表示范围，需要使用long存储。

# 构造ground-truth

如果你需要构造ground-truth，你可以修改`import-bulk.py`和`truth.py`的参数。

在`import-bulk.py`中，你可以修改以下参数：

- `input_path`: 这是一个字符串，表示输入数据的文件夹路径。在这个文件夹中，脚本会查找所有的文件，并将这些文件中的数据导入到数据库中。例如，如果`input_path`设置为`./osm/osm_10_4`，那么脚本会在`osm/osm_10_4`文件夹中查找所有的文件。

- `output_path`: 这是一个字符串，表示输出文件的文件夹路径。在这个文件夹中，脚本会将查询结果输出到对应的文件中。例如，如果`output_path`设置为`./query/knn/osm_10_4`，那么脚本会将查询结果输出到`query/knn/osm_10_4`文件夹中。

- `prefix`: 这是一个字符串，表示在数据库中创建的表的前缀，以及用于聚合所有表的视图的名称。例如，如果`prefix`设置为`osm`，那么在数据库中创建的表的名称将以`osm`为前缀，如`osm_1`、`osm_2`等，同时也会创建一个名为`osm`的视图，该视图将所有的`osm`表聚合在一起。

在`truth.py`中，你可以修改以下参数：

- `queries`: 这个参数是一个字典，其中的键是查询类型，值是对应的SQL查询语句。你可以根据需要添加或修改查询类型和查询语句。

- `output_path`: 这个参数是输出文件的路径。你可以修改这个参数来改变输出文件的位置。

- `global_view`: 这是多个表union出来的全局view。针对这个表可以完成所有表union的查询。

请注意，修改这些参数可能会影响到数据的导入和查询的结果，所以在修改参数前，请确保你了解这些参数的作用。