import logging
import os
import shutil
import sys
from datetime import datetime

import range_query
import secret_sum
import knn

sys.path.append('dependency/MP-SPDZ')

port = 11111

host = 'localhost'

base_path = './'

fh = logging.FileHandler(base_path + 'main.log')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG, handlers=[fh, ch])
logger = logging.getLogger(__name__)

input_path = base_path + 'input/Player'
output_path = base_path + 'output/Player'

network_config = base_path + 'config/range-query-network.txt'
data_length = 1

q_lng = 114.181114
q_lat = 22.3460861
# q_lng = 0
# q_lat = 0
def write_query_data_to_player0():
    with open(input_path + '0/Input-P0-0', 'w') as outfile:
        outfile.write(str(q_lng) + ' ' + str(q_lat))

write_query_data_to_player0()

import subprocess, shlex
from Compiler.compilerLib import Compiler
from party import Party

compiler = Compiler()
compiler.parser.add_option('--volume', dest='volume')
compiler.parser.add_option('--radius', default=0,  dest='radius')
compiler.parser.add_option('--k', default=0, dest='k')
compiler.parser.add_option('--n_clients', default=2, dest='n_clients')
compiler.parser.add_option('--program_name', default='knn', dest='program_name')
compiler.parser.add_option('--protocol', default='shamir', dest='protocol')
compiler.parse_args()


n_clients = int(compiler.options.n_clients)
program_name = compiler.options.program_name
# program_name = 'range_counting'
# program_name = 'knn'
protocol = compiler.options.protocol
# protocol = 'shamir'
# protocol = 'semi-ecdsa'


range_query.compile_range_query(compiler, data_length)
secret_sum.compile_secret_sum(compiler)
knn.compile_knn(compiler, data_length)

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
    milliseconds = execution_time.seconds * 1000 + int(execution_time.microseconds / 1000)
    seconds = execution_time.seconds + round(execution_time.microseconds / 1000000, 2)

    logger.info(f"Execution time: Seconds {seconds}s, Milliseconds {milliseconds} ms")
