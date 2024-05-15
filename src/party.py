from comsocket import ComSocket
import numpy as np
import math


class RandomSet():
    def __init__(self, input):
        self.input = input
        self.EPS = 1.0
        self.RANDOM_SET_SCALE = 0.5
        self.origin_size = len(self.input)
        self.random_size = math.ceil(self.origin_size * self.RANDOM_SET_SCALE + np.random.laplace(0, 1.0 / self.EPS))
        self.random_data = []
        self.sample_data = [int(np.random.laplace(0, 1.0 / self.EPS)), float(np.random.laplace(0, 1.0 / self.EPS)),
                            float(np.random.laplace(0, 1.0 / self.EPS))]

    def remove_random_data(self, input):
        output = []
        for array in input:
            if array not in self.random_data:
                output.append(array)
        return output

    def generate_random_data(self, input):
        output = input
        if len(input) == 0:
            for i in range(self.random_size):
                random_data = [int(np.random.laplace(0, 1.0 / self.EPS)), float(np.random.laplace(0, 1.0 / self.EPS)),
                               float(np.random.laplace(0, 1.0 / self.EPS))]
                self.random_data.append(random_data)
                output.append(random_data)
        else:
            for i in range(self.random_size):
                sample_input = input[i % len(input)]
                random_data = [sample_input[0] + int(np.random.laplace(0, 1.0 / self.EPS)),
                               sample_input[1] + float(np.random.laplace(0, 1.0 / self.EPS)),
                               sample_input[2] + float(np.random.laplace(0, 1.0 / self.EPS))]
                output.append(random_data)
                self.random_data.append(random_data)
        return output


class Party():
    def __init__(self, config_file, client_id, n_clients):
        self.config_file = config_file
        self.client_id = client_id
        self.n_clients = n_clients
        self.coms = ComSocket(config_file, self.client_id)

    def read_from_local(self, input_path):
        data = []
        with open(input_path, 'r') as file:
            for line in file.readlines():
                splits = line.strip().split()
                data.append([int(splits[0]), float(splits[1]), float(splits[2])])
        print("%d#local data %s\n" % (self.client_id, data))
        return data

    def mix(self, local_data: list, recv_data):
        output = []
        if recv_data is None:
            if len(local_data) == 0:
                pass
            else:
                output.extend(local_data)
        else:
            if len(local_data) == 0:
                output.extend(recv_data)
            else:
                output.extend(recv_data)
                output.extend(local_data)
        return output

    def secret_union(self, input_path):
        local_data = self.read_from_local(input_path)
        if self.client_id != 0:
            self.random_set = RandomSet(local_data)
            local_data = self.random_set.generate_random_data(local_data)

        if self.client_id == 0:
            union_data = self.coms.recv(self.n_clients - 1)
            print("%d#final union data %s" % (self.client_id, union_data[1]))

        elif self.client_id == 1:
            self.coms.send((self.client_id + 1) % self.n_clients, local_data)
            print("%d#send data to %d: %s" % (self.client_id, (self.client_id + 1) % self.n_clients, local_data))
            recv_data = self.coms.recv(self.n_clients - 1)
            print("%d#recv data from %d: %s" % (self.client_id, self.n_clients - 1, recv_data[1]))
            clean_data = self.random_set.remove_random_data(recv_data[1])
            self.coms.send((self.client_id + 1) % self.n_clients, clean_data)
            print("%d#send data to %d: %s" % (self.client_id, (self.client_id + 1) % self.n_clients, clean_data))
        elif self.client_id < self.n_clients - 1:
            recv_data = self.coms.recv(self.client_id - 1)
            print("%d#recv data from %d: %s" % (self.client_id, (self.client_id - 1) % self.n_clients, recv_data[1]))
            mix_data = self.mix(local_data, recv_data[1])
            self.coms.send((self.client_id + 1) % self.n_clients, mix_data)
            print("%d#send data to %d: %s" % (self.client_id, (self.client_id + 1) % self.n_clients, mix_data))
            recv_data = self.coms.recv(self.client_id - 1)
            print("%d#recv data from %d: %s" % (self.client_id, (self.client_id - 1) % self.n_clients, recv_data[1]))
            clean_data = self.random_set.remove_random_data(recv_data[1])
            self.coms.send((self.client_id + 1) % self.n_clients, clean_data)
            print("%d#send data to %d: %s" % (self.client_id, (self.client_id + 1) % self.n_clients, clean_data))
        else:
            recv_data = self.coms.recv(self.client_id - 1)
            print("%d#recv data from %d: %s" % (self.client_id, (self.client_id - 1) % self.n_clients, recv_data[1]))
            mix_data = self.mix(local_data, recv_data[1])
            self.coms.send(1, mix_data)
            print("%d#send data to %d: %s" % (self.client_id, 1, mix_data))

            recv_data = self.coms.recv(self.client_id - 1)
            print("%d#recv data from %d: %s" % (self.client_id, (self.client_id - 1) % self.n_clients, recv_data[1]))
            clean_data = self.random_set.remove_random_data(recv_data[1])
            self.coms.send(0, clean_data)
            print("%d#send data to %d: %s" % (self.client_id, 0, clean_data))

    def clean(self):
        self.coms.clean()


# random = RandomSet([[10, 1.1, 1.2], [2, 2.2, 2.3]])
# print("origin data%s", [[10, 1.1, 1.2], [2, 2.2, 2.3]])
# output = random.generate_random_data([[10, 1.1, 1.2], [2, 2.2, 2.3]])
# print("with random data %s", output)
# output = random.remove_random_data(output)
# print("remove random data %s", output)
