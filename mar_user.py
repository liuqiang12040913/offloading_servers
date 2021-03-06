
import socket, time, sys, struct, os, string, random, pickle
import requests
import numpy as np
import cv2

SERVER = '0.0.0.0'
LOCAL = '0.0.0.0'
USER_PORT = 9009

PKT_SIZE = 1000 # size of pkt in Bytes
SOCKET_TIME_OUT  =100 
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

def recv_image_from_socket(client, buffers):
    start_time = time.time() # time when recv starts
    # print("start buffers len: ", len(buffers))
    
    while len(buffers) < 8:
        try:
            buf = client.recv(1024)
        except:
            return False, 0, b''
        buffers += buf
        # if recv too long, then consider this user is disconnected
        if time.time() - start_time >= SOCKET_TIME_OUT:
            return False, 0, b''
        
    img_size_byte_pkt = buffers[:4] # here buffer could larger than 4 len
    img_id_byte_pkt = buffers[4:8] # here buffer could larger than 4 len
    buffers = buffers[8:] # here buffer could larger than 4 len

    size = int(img_size_byte_pkt.decode())
    id = int(img_id_byte_pkt.decode())
    # print("packet to be recvd: ", size)
    # print("middle remains len: ", len(buffers))

    while len(buffers) < size:
        try:
            buf = client.recv(1024)
        except:
            return False, 0, b''
        buffers += buf
        # if recv too long, then consider this user is disconnected
        if time.time() - start_time >= SOCKET_TIME_OUT:
            return False, 0, b''

    image_data = buffers[:size]
    buffers = buffers[size:]

    # print("late remains len: ", len(buffers))
    imgdata = image_data.decode()
    frame = imgdata

    return frame, id, buffers

if __name__ == "__main__":
    if len(sys.argv) == 3:
        SERVER = sys.argv[1]
        LOCAL = sys.argv[2]
    elif len(sys.argv) > 2:
        raise ValueError

    # bind to port to accept client
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.bind((LOCAL, 0))
    client.connect((SERVER,USER_PORT))
    
    X = cv2.imread('1.png')
    result, frame = cv2.imencode('.jpg', X, encode_param) 
    data_byte = pickle.dumps(frame, 0)
    size = len(data_byte)
    # main loop for all incoming client
    while True:
        start_time = time.time()
        client.sendall(struct.pack(">L", size) + data_byte)

        recv_data = client.recv(1024)

        delay = int(1000*(time.time() - start_time)) # ms 
        print("len:", size, 'delay:', delay)

        r = requests.post('http://'+SERVER+':'+str(USER_PORT+1000)+'/', data ={'perf':str(delay)}) 
        time.sleep(1)
        


            
