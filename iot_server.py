
import socket, time, sys, struct
import pickle, threading
import numpy as np
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from os import listdir
from os.path import isfile, join

HOST = '0.0.0.0'
USER_PORT = 9003
REST_PORT = 10003
BUFFER_SIZE = 256
SIZE = 100 # number of comparing images
SOCKET_TIME_OUT = 10
INFOS = [0.1]

server = FlaskAPI(__name__)

@server.route("/", methods=['GET'])
def function():
    global INFOS
    useful_len = int(len(INFOS)*0.2) # last 80%
    avg_data = np.mean(INFOS[useful_len:]) # get average 
    INFOS = [INFOS[-1]] # reset the data
    return str(avg_data), status.HTTP_200_OK

def recv_request_from_socket(client):
    start_time = time.time() # time when recv starts
    buffers = b''
    while len(buffers)<4:
        try:
            buf = client.recv(4-len(buffers))
        except:
            return False
        buffers += buf
        # if recv too long, then consider this user is disconnected
        if time.time() - start_time >= SOCKET_TIME_OUT:
            return False

    size, = struct.unpack('!i', buffers)
    print ("receiving %d bytes", size)
    recv_data = b''
    while len(recv_data) < size:
        try:
            data = client.recv(1024)
        except:
            return False
        recv_data += data
        # if recv too long, then consider this user is disconnected
        if time.time() - start_time >= SOCKET_TIME_OUT:
            return False

    frame_data = recv_data[:size]
    print ("recv data size: ", len(recv_data))

    recvdata = np.frombuffer(frame_data, dtype='uint8')

    return recvdata

def start_rest_api():
    server.run(host=HOST, port=REST_PORT)
    print('completed!')


if __name__ == "__main__":
    if len(sys.argv) == 1:
        PKT_SIZE = 1000
    elif len(sys.argv) == 2:
        PKT_SIZE = int(sys.argv[1])
    else:
        raise ValueError

    # start rest api server
    t1 = threading.Thread(target = start_rest_api)
    t1.setDaemon(True)
    t1.start()

    # bind to port to accept client
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((HOST,USER_PORT))
    s.listen(10)

    # main loop for all incoming client
    while True:
        print("waiting for client connection...")
        client, addr = s.accept()  # accept client
        client.settimeout(SOCKET_TIME_OUT)
        print ("Get new user socket")
    
        StartTime = time.time()
        # if client connected, keeping processing its data
        while True:
            size = recv_request_from_socket(client) # receive from client

            if size is False: 
                print("client droped, break, waiting other clients")
                break
            
            INFOS.append(time.time() - StartTime) # record info,  TODO XXX

            rgb = np.random.randint(0, 255, 3)
            # print(str(time.time() - StartTime), end=' ')  # print result

            real_data = str(rgb[0]) + ',' + str(rgb[1]) + ',' + str(rgb[2]) + ',\n'
            encode_real_data = real_data.encode()

            send_times = int(PKT_SIZE / len(encode_real_data))
            print(send_times, end=" ")
            encode_send_times = (str(send_times)+'\n').encode() # the size of first packet

            client.sendall(encode_send_times) # send first packet with size
            for idx in range(send_times):
                client.sendall(encode_real_data) # send back to client

            StartTime = time.time() # reset start time
        
        client.close()


            


