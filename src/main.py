port = 9000
protocol = 'shamir'
host = 'localhost'
n_clients = 4
input_path = './Player-Data/Input'
output_path = '../../output/OUTPUT'
log_path = '../../output/logs'
program = 'range_query'
network_config = '../../config/range-query-network.txt'

# program = 'range_counting'
# program = 'knn'

q_lng = 100.5532274
q_lat = 13.6985287
import subprocess, shlex
from Compiler.compilerLib import Compiler
from party import Party

compiler = Compiler()


# compiler.parser.add_option("-N", dest="nodes")
# compiler.parse_args()
# if compiler.options.nodes is None:
#     compiler.parser.error("-N is required")


@compiler.register_function('range_query')
def range_query():
    # 设置参与方数量和每方数据量, 0为查询方,1->silo为数据拥有方, radius为明文的查询半径
    silo = 3
    volume = 3
    radius = 6

    distance = radius * radius
    n = silo * volume

    from Compiler.library import print_ln, for_range, if_, print_ln_to, start_timer, stop_timer
    from Compiler.types import sfix, sfix, cint, regint, Array, sint, Matrix

    # 设置定点数精度
    sfix.set_precision(16, 32)

    # 创建输入数据数组
    data_id = Matrix(silo, volume, sint)
    data_lng = Matrix(silo, volume, sfix)
    data_lat = Matrix(silo, volume, sfix)

    # 查询方0输入查询数据
    q_lng = sfix.get_input_from(0)
    q_lat = sfix.get_input_from(0)

    start_timer(1)

    @for_range(silo)
    def _(i):
        for j in range(volume):
            data_id[i][j] = sint.get_input_from(i + 1)
            data_lng[i][j] = sfix.get_input_from(i + 1)
            data_lat[i][j] = sfix.get_input_from(i + 1)

    import math

    @for_range(1, silo + 1)
    def _(i):
        for j in range(volume):
            acc = sint(0)
            acc += (data_lng[i - 1][j] - q_lng).square()
            acc += (data_lat[i - 1][j] - q_lat).square()
            acc -= distance

            inside = (acc < 0)

            @if_(inside.reveal())
            # 满足距离条件
            def _():
                print_ln_to(i, '%s %s %s', data_id[i - 1][j].reveal_to(i), data_lng[i - 1][j].reveal_to(i),
                            data_lat[i - 1][j].reveal_to(i))

    stop_timer(1)


@compiler.register_function('range_counting')
def range_counting():
    # 设置参与方数量和每方数据量, 0为查询方,1->silo为数据拥有方, radius为明文的查询半径
    silo = 3
    volume = 3
    radius = 6
    distance = radius * radius

    n = silo * volume

    from Compiler.library import print_ln, for_range, if_, print_ln_to, start_timer, stop_timer
    from Compiler.types import sfix, sfix, cint, regint, Array, sint, Matrix
    # 设置定点数精度
    sfix.set_precision(16, 32)

    # 创建输入数据数组
    data_id = Matrix(silo, volume, sint)
    data_lng = Matrix(silo, volume, sfix)
    data_lat = Matrix(silo, volume, sfix)

    # 查询方0输入查询数据
    q_lng = sfix.get_input_from(0)
    q_lat = sfix.get_input_from(0)

    @for_range(silo)
    def _(i):
        for j in range(volume):
            data_id[i][j] = sint.get_input_from(i + 1)
            data_lng[i][j] = sfix.get_input_from(i + 1)
            data_lat[i][j] = sfix.get_input_from(i + 1)

    import math

    start_timer(1)

    count = sint.Array(silo)

    @for_range(silo)
    def _(i):
        local_count = cint(0)
        for j in range(volume):
            t = ((data_lng[i][j] - q_lng).square() + (data_lat[i][j] - q_lat).square() <= distance).if_else(1, 0)

            @if_(t.reveal() == 1)
            def _():
                local_count.update(local_count + 1)
        count[i] = local_count

    # 输出结果
    print_ln_to(0, "%s", sum(count[i] for i in range(silo)).reveal_to(0))
    stop_timer(1)


@compiler.register_function('knn')
def knn():
    MAX_DISTANCE = 9999
    # 设置参与方数量和每方数据量, 0为查询方,1->silo为数据拥有方, k为kNN的参数
    silo = 3
    volume = 3
    k = 5

    from Compiler.library import print_ln, for_range, if_, print_ln_to, start_timer, stop_timer
    from Compiler.types import sfix, sfix, cint, regint, Array, sint, Matrix
    # 设置定点数精度
    sfix.set_precision(16, 32)

    # 创建输入数据数组
    data_id = Matrix(silo, volume, sint)
    data_lng = Matrix(silo, volume, sfix)
    data_lat = Matrix(silo, volume, sfix)

    # 查询方0输入查询数据
    q_lng = sfix.get_input_from(0)
    q_lat = sfix.get_input_from(0)

    k_player_array = cint.Array(k)
    k_id_array = sint.Array(k)
    k_lng_array = sint.Array(k)
    k_lat_array = sint.Array(k)

    k_distance_array = sfix.Array(k)
    k_distance_array.assign_all(MAX_DISTANCE)

    @for_range(silo)
    def _(i):
        for j in range(volume):
            data_id[i][j] = sint.get_input_from(i + 1)
            data_lng[i][j] = sfix.get_input_from(i + 1)
            data_lat[i][j] = sfix.get_input_from(i + 1)

    import math

    @for_range(silo)
    def _(i):
        for j in range(volume):
            distance = (data_lng[i][j] - q_lng).square() + (data_lat[i][j] - q_lat).square()
            max_k = cint(0)
            for kk in range(1, k):
                t = (k_distance_array[max_k] < k_distance_array[kk]).if_else(1, 0)

                @if_(t.reveal() == 1)
                def _():
                    max_k.update(kk)
            t = (distance < k_distance_array[max_k]).if_else(1, 0)

            @if_(t.reveal() == 1)
            def _():
                k_player_array[max_k] = i
                k_id_array[max_k] = data_id[i][j]
                k_distance_array[max_k] = distance
                k_lng_array[max_k] = data_lng[i][j]
                k_lat_array[max_k] = data_lat[i][j]

    # 输出结果
    @for_range(k)
    def _(i):
        player_id = k_player_array[i] + 1
        print_ln_to(player_id, "%s %s %s", k_id_array[i].reveal_to(player_id),
                    k_lng_array[i].reveal_to(player_id), k_lat_array[i].reveal_to(player_id))

    stop_timer(1)


import threading


def write_data_to_player0():
    with open(input_path + '-P0-0', 'w') as outfile:
        outfile.write(str(q_lng) + ' ' + str(q_lat))


def start_party_node(i, network_config, n_clients, input_file, log_file):
    node = Party(network_config, i, n_clients=n_clients)
    node.secret_union(input_file)
    node.clean()
    # with open(log_file, 'a') as outfile:
    #     print("Node {} started".format(i), file=outfile)


def main():
    write_data_to_player0()

    compiler.compile_func()

    cmd_str = '{}/{}-party.x -N {} -p {} -h {} -pn {} -IF {} -OF {} {} -v'
    log_str = '{}/LOG-P{}.log'
    process_pool = []
    for i in range(n_clients):
        cmd = cmd_str.format('.', protocol, n_clients, i, host,
                             port, input_path, output_path, program)
        print(cmd)
        with open(log_str.format(log_path, i), 'w') as outfile:
            cmd_i = shlex.split(cmd)
            process_pool.append(subprocess.Popen(cmd_i, stdout=outfile, stderr=outfile))

    for i in range(n_clients):
        process_pool[i].wait()

    for i in range(n_clients):
        threading.Thread(target=start_party_node, args=(
        i, network_config, n_clients, output_path + '-P' + str(i) + '-0', log_str.format(log_path, i))).start()


if __name__ == '__main__':
    main()
