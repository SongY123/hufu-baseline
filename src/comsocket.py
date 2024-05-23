import pickle, struct, socket
import time
import logging

logger = logging.getLogger(__name__)

class ComSocket():
    def __init__(self, config_file: str, client_id: int):
        client_id = int(client_id)
        ip_list = {}
        with open(config_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                ip, port = line.split(' ')
                port = int(port)
                ip_list[i] = (ip, port)
        self.ip_list = ip_list
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', ip_list[client_id][1]))
        self.socket.listen()
        self.connections = {}
        #connect
        for i in range(client_id):
            while True:
                try:
                    s = socket.socket()
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    s.connect(ip_list[i])
                    self.send(s, client_id)
                    self.connections[i] = s
                    logger.debug("%d#connect to client %d success" % (client_id, i))
                    break
                except Exception as e:
                    time.sleep(0.01)
        #accept
        for i in range(client_id + 1, len(ip_list)):
            conn, addr = self.socket.accept()
            _, cid = self.recv(conn)
            self.connections[cid] = conn
            logger.debug("%d#client %d connected" % (client_id, i))
    
    def send(self, conn, message):
        if type(conn) == int:
            conn = self.connections[conn]
        message = pickle.dumps(message)
        data_len = len(message)
        header = struct.pack('i', data_len)
        conn.send(header)
        conn.send(message)
        return data_len
    
    def recv(self, conn):
        if type(conn) == int:
            conn = self.connections[conn]
        data_len = conn.recv(4, socket.MSG_WAITALL)
        if not data_len: return None
        data_len = struct.unpack('i', data_len)[0]
        recv_data = conn.recv(data_len, socket.MSG_WAITALL)
        return data_len, pickle.loads(recv_data)

    def clean(self):
        for key, value in self.connections.items():
            self.connections[key].close()
        self.socket.close()
