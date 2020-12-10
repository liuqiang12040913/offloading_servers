
import socket, time, sys, struct, os
import cv2, pickle, threading
import numpy as np
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from os import listdir
from os.path import isfile, join

HOST = '0.0.0.0'
USER_PORT = 9001
REST_PORT = 10001
BUFFER_SIZE = 256
SIZE = 100 # number of comparing images
SOCKET_TIME_OUT = 10
INFOS = [0.1]
FOLDER = 'images/'
CWD = os.getcwd()

server = FlaskAPI(__name__)

@server.route("/", methods=['GET'])
def function():
    global INFOS
    avg_data = np.mean(INFOS) # get average 
    INFOS = [INFOS[-1]] # reset the data
    return {'data':avg_data}, status.HTTP_200_OK

def recv_image_from_socket(client):
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
    #print "receiving %d bytes" % size
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

    imgdata = np.frombuffer(frame_data, dtype='uint8')
    decimg = cv2.imdecode(imgdata,1)

    return decimg


def process(feature_extractor, matcher, image):

    latent = feature_extractor.inference(image)    
    obj_id = sub_process_matching(latent, global_database, matcher)

    return obj_id


class ORB:
    def __init__(self,):
        # Initiate ORB detector
        self.orb = cv2.ORB_create(edgeThreshold=3)
        # the default edgethreshold is 31, cannot detect keypoints
        # which is not suitable for small cropped image
        # reduce this value can apply to small image

    def inference(self, img):
        # find the keypoints with ORB
        kp = self.orb.detect(img, None)
        # compute the descriptors with ORB
        kp, des = self.orb.compute(img, kp)
        
        if des is None:
            # if no feature detected, then randomly generated 100 features.
            des = np.random.randint(0, 100, (100, 32), dtype=np.uint8)

        return des


def sub_process_matching(features, global_database, matcher):
    # given an object (loc, latent), find the corresponding object in global_database
    # the geo-distance should be smaller than NEARBY_DIST, and then find the minimum latent one
    # if not found, then report a new object detected.
    obj_id, min_aug_dist = 0, 1e9

    for key, latent in global_database.items():
        # where latent vector could be just a vector or a multi-vector due to orb detection            
        matches = matcher.match(latent, features) # store the latent dist
        avg_distance = np.mean([match.distance for match in matches])
            
        if avg_distance <= min_aug_dist: # if geo loc is nearby and aug-distance is smaller
            min_aug_dist = avg_distance
            obj_id = key

    return obj_id


def start_rest_api():
    server.run(host=HOST,port=REST_PORT)
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

    # init some objects
    feature_extractor = ORB()
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # global_database = {}
    # # get all images
    # images = [cv2.imread(FOLDER+f) for f in listdir(FOLDER) if isfile(join(FOLDER, f))]

    # # save to global images
    # for i, img in enumerate(images):
    #     latent = feature_extractor.inference(img)
    #     global_database[str(i)] = latent

    # with open('global_database.pkl', 'wb') as handler:
    #     pickle.dump(global_database, handler)
    #### handle different folders #####
    try:
        with open(CWD+'/global_database.pkl', 'rb') as handler:
            global_database = pickle.load(handler)
    except: pass
    try:
        with open(CWD+'offloading_servers/global_database.pkl', 'rb') as handler:
            global_database = pickle.load(handler)
    except: pass 
    try:
        with open('global_database.pkl', 'rb') as handler:
            global_database = pickle.load(handler)
    except: pass 
    print(len(global_database)) # if no global_database loaded, then report error
    # main loop for all incoming client
    while True:
        print("waiting for client connection...")
        client, addr = s.accept()  # accept client
        client.settimeout(5)
        print ("Get new user socket")
    

        StartTime = time.time()
        # if client connected, keeping processing its data
        while True:
            decimg = recv_image_from_socket(client) # receive from client

            if decimg is False: 
                print("client droped, break, waiting other clients")
                break
            
            ProcessTime = time.time()
            match_id = process(feature_extractor, matcher, decimg) # process the img
            print(str(time.time() - ProcessTime), end=' ')  # print result

            INFOS.append(time.time() - StartTime) # record info, latency

            # print(str(time.time() - StartTime), end=' ')  # print result

            str1 = str(match_id) + '\n'  # prepare data

            client.sendall(str1.encode()) # send back to client

            StartTime = time.time() # reset start time
        
        client.close()


            


