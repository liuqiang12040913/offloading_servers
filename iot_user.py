
import socket, time, sys, struct, os, string, random
import numpy as np

HOST = '0.0.0.0'
USER_PORT = 9009

PKT_SIZE = 1000 # size of pkt in Bytes
SOCKET_TIME_OUT  =100 

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
    if len(sys.argv) == 2:
        HOST = sys.argv[1]
    elif len(sys.argv) > 2:
        raise ValueError

    # bind to port to accept client
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((HOST,USER_PORT))
    
    id = 1000
    buffers = b''
    # main loop for all incoming client
    while True:
        data = ''.join(random.choices(string.ascii_uppercase + string.digits, k = PKT_SIZE))
            
        data_byte = data.encode()
        send_len = len(data_byte)
        
        client.sendall(str(send_len).encode()) # send back to client
        client.sendall(str(id).encode()) # send back to client

        client.sendall(data_byte) # send back to client

        _, id, buffers = recv_image_from_socket(client, buffers)

        print(id)
        id = np.random.randint(1000,9999)

        time.sleep(1)
        


            
