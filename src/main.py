import os
import shutil
from datetime import datetime
import logging

port = 11111
# protocol = 'shamir'
protocol = 'semi-ecdsa'
host = 'localhost'
n_clients = 4
base_path = '../../'

fh = logging.FileHandler(base_path + 'main.log')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG, handlers=[fh, ch])
logger = logging.getLogger(__name__)

input_path = base_path + 'input/Player'

output_path = base_path + 'output/Player'

program_name = 'range_query'
# program_name = 'range_counting'
# program_name = 'knn'
network_config = base_path + 'config/range-query-network.txt'
data_length = 1

q_lng = 114.181114
q_lat = 22.3460861
# q_lng = 0
# q_lat = 0
def write_data_to_player0():
    with open(input_path + '0/Input-P0-0', 'w') as outfile:
        outfile.write(str(q_lng) + ' ' + str(q_lat))

write_data_to_player0()

import subprocess, shlex
from Compiler.compilerLib import Compiler
from party import Party

compiler = Compiler()
compiler.parser.add_option('--volume', dest='volume')
compiler.parser.add_option('--radius', default=0,  dest='radius')
compiler.parser.add_option('--k', default=0, dest='k')
compiler.parse_args()


@compiler.register_function('range_query')
def range_query():

    from Compiler.types import sint, regint, Array, MemValue, sfix, cint
    from Compiler.library import print_ln, print_ln_to, do_while, for_range, if_

    # 设置定点数精度
    sfix.set_precision(32, 64)

    # 设置参与方数量和每方数据量, 0为查询方,1->silo为数据拥有方, radius为明文的查询半径
    volume = int(compiler.options.volume)

    radius = float(compiler.options.radius)
    distance = radius * radius

    def main():
        q_lng = sfix.get_input_from(0)
        q_lat = sfix.get_input_from(0)

        def game_loop(_=None):
            def type_run():
                id = sint.get_input_from(1)
                lng = sfix.get_input_from(1)
                lat = sfix.get_input_from(1)
                acc = sint(0)
                acc += (lng - q_lng).square()
                acc += (lat - q_lat).square()
                acc -= distance
                inside = (acc < 0)

                @if_(inside.reveal())
                def _():
                    # print_ln("%s", id.reveal())
                    if data_length == 3:
                        print_ln_to(1, "%s %s %s", id.reveal_to(1), lng.reveal_to(1), lat.reveal_to(1))
                    else:
                        print_ln_to(1, "%s", id.reveal_to(1))

            type_run()
            return True

        logger.info('run %d volume' % volume)
        for_range(volume)(game_loop)

    main()

compiler.compile_func()

@compiler.register_function('secret_sum')
def secret_sum():
    silo = n_clients

    from Compiler.library import print_ln, for_range, if_, print_ln_to, start_timer, stop_timer
    from Compiler.types import sfix, sfix, cint, regint, Array, sint, Matrix
    # 设置定点数精度
    start_timer(1)

    count = sint.Array(silo - 1)
    @for_range(silo - 1)
    def _(i):
        count[i] = sint.get_input_from(i + 1)

    # 输出结果
    print_ln_to(0, "%s", sum(count[i] for i in range(silo - 1)).reveal_to(0))
    stop_timer(1)

compiler.compile_func()

@compiler.register_function('knn')
def knn():
    MAX_DISTANCE = 9999
    # 设置参与方数量和每方数据量, 0为查询方,1->silo为数据拥有方, k为kNN的参数
    silo = n_clients - 1
    volume = int(compiler.options.volume)
    k = int(compiler.options.k)

    from Compiler.library import print_ln, for_range, if_, print_ln_to, start_timer, stop_timer
    from Compiler.types import sfix, sfix, cint, regint, Array, sint, Matrix
    # 设置定点数精度
    sfix.set_precision(16, 32)

    def main():
        # 查询方0输入查询数据
        q_lng = sfix.get_input_from(0)
        q_lat = sfix.get_input_from(0)
        k_player_array = cint.Array(k)
        k_id_array = sint.Array(k)
        k_lng_array = sint.Array(k)
        k_lat_array = sint.Array(k)

        k_distance_array = sfix.Array(k)
        k_distance_array.assign_all(MAX_DISTANCE)

        import math

        def game_loop(_=None):
            def type_run():
                @for_range(silo - 1)
                def _(i):
                    id = sint.get_input_from(i + 1)
                    lng = sfix.get_input_from(i + 1)
                    lat = sfix.get_input_from(i + 1)
                    distance = (lng - q_lng).square() + (lat - q_lat).square()
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
                        k_id_array[max_k] = id
                        k_distance_array[max_k] = distance
                        k_lng_array[max_k] = lng
                        k_lat_array[max_k] = lat
            type_run()
            return True

        logger.info('run %d volume' % volume)
        for_range(volume)(game_loop)

        @for_range(k)
        def _(i):
            player_id = k_player_array[i] + 1
            if data_length == 3:
                print_ln_to(player_id, "%s %s %s", k_id_array[i].reveal_to(player_id),
                            k_lng_array[i].reveal_to(player_id), k_lat_array[i].reveal_to(player_id))
            else:
                print_ln_to(player_id, "%s", k_id_array[i].reveal_to(player_id))

    start_timer(1)
    main()
    stop_timer(1)

compiler.compile_func()

import threading


def start_party_node(i, network_config, n_clients, input_file, data_length, log_file=None):
    node = Party(network_config, i, n_clients=n_clients, data_length=data_length)
    node.secret_union(input_file)
    node.clean()
    # with open(log_file, 'a') as outfile:
    #     print("Node {} started".format(i), file=outfile)

def union_worker(i):
    if program_name == 'knn':
        output_file = output_path + str(i) + os.sep + 'Output-P' + str(i) + '-0'
    else:
        if i == 0:
            output_file = output_path + str(i) + os.sep + 'Output-P' + str(0) + '-0'
        else:
            output_file = output_path + str(i) + os.sep + 'Output-P' + str(1) + '-0'
    start_party_node(i, network_config, n_clients, output_file, data_length)

def main(program_name=None):
    if program_name == 'range_counting' or program_name == 'range_query':
        program = 'range_query'
    elif program_name == 'knn':
        program = 'knn'
    cmd_str = '{}/{}-party.x -N {} -p {} -h {} -pn {} -IF {} -OF {} {} -v'
    process_pool = []
    if program_name == 'knn':
        for i in range(2, n_clients):
            shutil.copy2(input_path + str(i) + os.sep + 'Input-P1-0', input_path + str(i) + os.sep + 'Input-P' + str(i) + '-0')
        for i in range(n_clients):
            player_input_path = input_path + str(i) + os.sep + 'Input'
            player_output_path = output_path + str(i) + os.sep + 'Output'


            cmd = cmd_str.format(base_path + 'dependency/MP-SPDZ', protocol, n_clients, i, host,
                           port, player_input_path, player_output_path, program)

            logger.info(cmd)
            with open(output_path + str(i) + os.sep + 'Log-P' + str(i) + '.log', 'w') as outfile:
                cmd_i = shlex.split(cmd)
                process_pool.append(subprocess.Popen(cmd_i, stdout=outfile, stderr=outfile))
    else:
        for i in range(1, n_clients):
            player0_input_path = input_path + str(0) + os.sep + 'Input'
            player1_input_path = input_path + str(i) + os.sep + 'Input'
            player0_output_path = output_path + str(0) + os.sep + 'Output'
            player1_output_path = output_path + str(i) + os.sep + 'Output'
            cmd = cmd_str.format(base_path + 'dependency/MP-SPDZ', protocol, 2, 0, host,
                           port + i + i, player0_input_path, player0_output_path, program)
            logger.info(cmd)
            player0_log_path = output_path + str(0) + os.sep + 'Log-P0-' + str(i) + '.log'
            player1_log_path = output_path + str(i) + os.sep + 'Log-P' + str(i) + '.log'

            with open(player0_log_path, 'w') as outfile:
                cmd_i = shlex.split(cmd)
                process_pool.append(subprocess.Popen(cmd_i, stdout=outfile, stderr=outfile))

            cmd = cmd_str.format(base_path + 'dependency/MP-SPDZ', protocol, 2, 1, host,
                           port + i + i, player1_input_path, player1_output_path, program)

            logger.info(cmd)
            with open(player1_log_path, 'w') as outfile:
                cmd_i = shlex.split(cmd)
                process_pool.append(subprocess.Popen(cmd_i, stdout=outfile, stderr=outfile))

    for i in range(n_clients):
        process_pool[i].wait()

    if program_name == 'range_counting':
        # rewrite result to player
        for i in range(n_clients):
            if i == 0:
                origin_output = output_path + str(i) + os.sep + 'Output-P0-0'
            else:
                origin_output = output_path + str(i) + os.sep + 'Output-P1-0'
            new_input = output_path + str(i) + os.sep + 'Input'
            new_output = output_path + str(i) + os.sep + 'New-Output'
            new_log_path = output_path + str(i) + os.sep + 'NEWLog-P' + str(i) + '.log'
            with open(origin_output, 'r') as src_file:
                lines = src_file.readlines()

            line_count = len(lines)

            with open(new_input + '-P' + str(i) + '-0', 'w') as dst_file:
                dst_file.write(str(line_count))

            cmd = cmd_str.format(base_path + 'dependency/MP-SPDZ', protocol, n_clients, i, host,
                                 port, new_input, new_output, 'secret_sum')
            logger.info(cmd)

            with open(new_log_path, 'w') as outfile:
                cmd_i = shlex.split(cmd)
                process_pool.append(subprocess.Popen(cmd_i, stdout=outfile, stderr=outfile))

    else:
        union_process_pool = []
        for i in range(n_clients):
            t = threading.Thread(target=union_worker, args=(i,))
            t.start()
            union_process_pool.append(t)

        for t in union_process_pool:
            t.join()


if __name__ == '__main__':
    start_time = datetime.now()

    main(program_name)

    end_time = datetime.now()
    execution_time = end_time - start_time
    milliseconds = int(execution_time.microseconds / 1000)
    seconds = round(execution_time.microseconds / 1000000, 2)

    logger.info(f"Execution time: Seconds {seconds}s, Milliseconds {milliseconds} ms")
