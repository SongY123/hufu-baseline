# Run the project
## Compile
```shell
# cd dependency/MP-SPDZ
make setup
make
# protocol=shamir
# protocol=hemi
make -j8 $protocal-party.x
```

## Setup
```shell
sh dependency/MP-SPDZ/Scripts/setup-ssl.sh <n_clients>
LD_LIBRARY_PATH=<SPDZ-ROOT-DIR>
DYLD_LIBRARY_PATH=<SPDZ-ROOT-DIR>
```
## Run
```shell
PROTOCOL=<hemi/shamir> 
PROGRAM_NAME=<range_query/range_counting/knn/distance_join/knn_join>

cd hufu-baseline
python src/main.py --volume <VOLUME> --radius <RADIUS> --n_clients <N_CLIENTS> --program_name PROGRAM_NAME --protocol <PROTOCOL>
python src/main.py --volume <VOLUME> --radius <RADIUS> --n_clients <N_CLIENTS> --program_name PROGRAM_NAME --protocol <PROTOCOL>
python src/main.py --volume <VOLUME> --k <K> --n_clients <N_CLIENTS> --program_name PROGRAM_NAME --protocol <PROTOCOL>
```
# Query
* Range Query
* Range Counting
* kNN
* Distance Join
* kNN Join