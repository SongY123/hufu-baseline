from comsocket import ComSocket
import numpy as np
import math
import logging

logger = logging.getLogger(__name__)
class RandomSet():
    def __init__(self, data: list, data_length=3):
        self.data = data
        self.data_length = data_length
        self.EPS = 1.0
        self.RANDOM_SET_SCALE = 0.5
        self.origin_size = len(self.data)
        self.random_size = math.ceil(self.origin_size * self.RANDOM_SET_SCALE + np.random.laplace(0, 1.0 / self.EPS))
        self.random_data = []
        if self.data_length == 1:
            self.sample_data = [int(np.random.laplace(0, 1.0 / self.EPS))]
        else:
            self.sample_data = [int(np.random.laplace(0, 1.0 / self.EPS)), float(np.random.laplace(0, 1.0 / self.EPS)),
                                float(np.random.laplace(0, 1.0 / self.EPS))]

    def update_data(self, new_data):
        self.data = new_data

    def remove_random_data(self):
        for array in reversed(self.data):
            if array in self.random_data:
                self.random_data.remove(array)  # ensure the array is removed only once
                self.data.remove(array)

    def generate_random_data(self):
        if len(self.data) == 0:
            for i in range(self.random_size):
                if self.data_length == 1:
                    random_data = [int(np.random.laplace(0, 1.0 / self.EPS))]
                else:
                    random_data = [int(np.random.laplace(0, 1.0 / self.EPS)),
                                   float(np.random.laplace(0, 1.0 / self.EPS)),
                                   float(np.random.laplace(0, 1.0 / self.EPS))]
                self.random_data.append(random_data)
                self.data.append(random_data)
        else:
            for i in range(self.random_size):
                sample_input = self.data[i % len(self.data)]
                if self.data_length == 1:
                    random_data = [sample_input[0] + int(np.random.laplace(0, 1.0 / self.EPS))]
                else:
                    random_data = [sample_input[0] + int(np.random.laplace(0, 1.0 / self.EPS)),
                                   sample_input[1] + float(np.random.laplace(0, 1.0 / self.EPS)),
                                   sample_input[2] + float(np.random.laplace(0, 1.0 / self.EPS))]
                self.data.append(random_data)
                self.random_data.append(random_data)


class Party():
    def __init__(self, config_file, client_id, n_clients, data_length):
        self.config_file = config_file
        self.client_id = client_id
        self.n_clients = n_clients
        self.data_length = data_length
        self.coms = ComSocket(config_file, self.client_id)

    def read_from_local(self, input_path):
        data = []
        with open(input_path, 'r') as file:
            for line in file.readlines():
                splits = line.strip().split()
                if len(splits) == 1:
                    data.append([int(splits[0])])
                elif len(splits) == 3:
                    data.append([int(splits[0]), float(splits[1]), float(splits[2])])
                else:
                    raise ValueError("Data length mismatched! Should be 1 or 3.")
        logger.debug("%d#local data %s" % (self.client_id, data))
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

    def process_data(self, recv_from, send_to):
        recv_data = self.coms.recv(recv_from)
        logger.debug("%d#recv data from %d: %s" % (self.client_id, recv_from, recv_data[1]))
        self.random_set.update_data(recv_data[1])
        self.random_set.remove_random_data()
        self.coms.send(send_to, self.random_set.data)
        logger.debug("%d#send data to %d: %s" % (self.client_id, send_to, self.random_set.data))

    def secret_union(self, input_path):
        local_data = self.read_from_local(input_path)
        if self.client_id != 0:
            self.random_set = RandomSet(local_data, self.data_length)
            self.random_set.generate_random_data()

        if self.client_id == 0:
            union_data = self.coms.recv(self.n_clients - 1)
            logger.info("%d#final union data %s" % (self.client_id, union_data[1]))

        elif self.client_id == 1:
            self.coms.send((self.client_id + 1) % self.n_clients, self.random_set.data)
            logger.debug("%d#send data to %d: %s" % (
                self.client_id, (self.client_id + 1) % self.n_clients, self.random_set.data))
            self.process_data(self.n_clients - 1, (self.client_id + 1) % self.n_clients)

        elif self.client_id < self.n_clients - 1:
            recv_data = self.coms.recv(self.client_id - 1)
            logger.debug("%d#recv data from %d: %s" % (self.client_id, (self.client_id - 1) % self.n_clients, recv_data[1]))
            mix_data = self.mix(self.random_set.data, recv_data[1])
            self.coms.send((self.client_id + 1) % self.n_clients, mix_data)
            logger.debug("%d#send data to %d: %s" % (self.client_id, (self.client_id + 1) % self.n_clients, mix_data))
            self.process_data(self.client_id - 1, (self.client_id + 1) % self.n_clients)

        else:
            recv_data = self.coms.recv(self.client_id - 1)
            logger.debug("%d#recv data from %d: %s" % (self.client_id, (self.client_id - 1) % self.n_clients, recv_data[1]))
            mix_data = self.mix(self.random_set.data, recv_data[1])
            self.coms.send(1, mix_data)
            logger.debug("%d#send data to %d: %s" % (self.client_id, 1, mix_data))
            self.process_data(self.client_id - 1, 0)

    def clean(self):
        self.coms.clean()
