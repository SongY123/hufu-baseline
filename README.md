# Run the project
## compile
```shell
# cd dependency/MP-SPDZ
make setup
# protocol=shamir
make -j8 $protocal-party.x
# nparties=4
Scripts/setup-ssl.sh $nparties
```

## 运行
```shell
scripts/run.sh
```
# Query
* Range Query
* Range Counting
* kNN
