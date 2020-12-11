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
VIDEO_PATH = '/1.mp4'

rtmp_server = 'rtmp://'+HOST+'/LiveApp/1'
INFOS = [10]

server = FlaskAPI(__name__)

@server.route("/", methods=['GET'])
def function():
    global INFOS
    avg_data = np.mean(INFOS) # get average 
    INFOS = [INFOS[-1]] # reset the data
    return str(avg_data), status.HTTP_200_OK

def start_ffmpeg_stream():
    command = 'ffmpeg -re -i ' + VIDEO_PATH + ' -c copy -f flv ' + rtmp_server
    while True:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    print('completed!')

def start_rest_api():
    server.run(host=HOST,port=REST_PORT)
    print('completed!')
   
def recv_request_from_socket(client):
    start_time = time.time() # time when recv starts
    buffers = b''
    while len(buffers)<4:
        try:
            buf = client.recv(4)
        except:
            return False
        buffers += buf
        # if recv too long, then consider this user is disconnected
        if time.time() - start_time >= SOCKET_TIME_OUT:
            return False

    size, = struct.unpack('!i', buffers)

    return size

if __name__ == "__main__":

    # start rest api server
    t0 = threading.Thread(target = start_ffmpeg_stream)
    t0.setDaemon(True)
    t0.start()
    
    # start rest api server
    t1 = threading.Thread(target = start_rest_api)
    t1.setDaemon(True)
    t1.start()

    FPS = 0

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
            fps = recv_request_from_socket(client) # receive from client

            if fps is False: 
                print("client droped, break, waiting other clients")
                break
            
            INFOS.append(fps) # record info, 

            print(fps)  # print result

            # reply_data = '8,8,8,\n'

            # client.sendall(reply_data.encode()) # send back to client

            StartTime = time.time() # reset start time
        
        client.close()






# output = output.decode('utf-8').split() ## read then decode next split with default ''

# import ffmpeg
# # stream = ffmpeg.input(rtmp_server)
# # stream = ffmpeg.output(stream, 'o.mp4')
# # ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

# process = (
# ffmpeg
#         .input(rtmp_server)
#         .output('pipe:', format='flv')
#         .run_async(pipe_stdout=True)
# )

# while True:
#     in_bytes = process.stdout.readline()
#     if not in_bytes:
#         break
#     else:
#         print(in_bytes.decode('utf-8'))



# command = 'ffprobe  -select_streams v:1 -show_entries stream=r_frame_rate -i ' + rtmp_server

# #output = subprocess.check_output(strs.split())
# proc = subprocess.Popen('ffprobe  -select_streams v:1 -show_entries stream=r_frame_rate -i ' + rtmp_server, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# output = proc.stdout.read().decode('utf-8').split() ## read then decode next split with default ''

# for i, out in enumerate(output):
#     idx = out.find('fps')
#     if idx != -1: break

# try:
#     fps = float(output[i-1])
# except:
#     fps = 10.0

# print(fps)

# print(time.time() - start_time)

# print('done!')
