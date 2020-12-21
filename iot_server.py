
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
    avg_data = np.mean(INFOS) # get average 
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

    return size

def start_rest_api():
    server.run(host=HOST, port=REST_PORT)
    print('completed!')


if __name__ == "__main__":

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

            tmp_data = str(rgb[0]) + ',' + str(rgb[1]) + ',' + str(rgb[2])+ ','
            reply_data = tmp_data * 20 + '\n'  # prepare data, 128 bytes

            client.sendall(reply_data.encode()) # send back to client

            StartTime = time.time() # reset start time
        
        client.close()


            


