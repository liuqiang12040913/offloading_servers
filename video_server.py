import socket, time, sys, struct
import string, time
import subprocess
import threading
import numpy as np
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

HOST = '0.0.0.0'
USER_PORT = 9002
REST_PORT = 10002
BUFFER_SIZE = 256
SOCKET_TIME_OUT = 10
VIDEO_PATH = '/'
Default_HET = 200

rtmp_server = 'rtmp://192.168.17.10/live/test'
HET = [Default_HET]

server = FlaskAPI(__name__)

@server.route("/", methods=['GET'])
def function():
    global HET
    print(np.mean(HET))
    avg_het = HET[-1]
    HET = [HET[-1]]
    return str(avg_het), status.HTTP_200_OK
def start_ffmpeg_stream():
    global HET
    while True:
        command = 'ffmpeg -re -i ' + VIDEO_PATH + 'test.mp4 -c copy -f flv ' + rtmp_server

        process = subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

def start_rest_api():
    server.run(host=HOST,port=REST_PORT)
    print('completed!')

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
if __name__ == "__main__":

    # # start rest api server
    # t0 = threading.Thread(target = start_ffmpeg_stream)
    # t0.setDaemon(True)
    # t0.start()

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
        count = 0

        StartTime = time.time()
        # if client connected, keeping processing its data
        while True:
            het = recv_request_from_socket(client) # receive from client

            if het is False:
                HET.append(Default_HET)
                print("client droped, break, waiting other clients")
                break

            HET.append(het)  # record the fps

            reply_data = '8\n'

            client.sendall(reply_data.encode()) # send back to client

            StartTime = time.time() # reset start time
            count += 1

        client.close()



