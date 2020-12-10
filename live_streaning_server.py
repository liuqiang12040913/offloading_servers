import subprocess
import string, time
import threading
import numpy as np
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

HOST = '0.0.0.0'
REST_PORT = 9999

rtmp_server = 'rtmp://127.0.0.1/LiveApp/v'
STREAM_FPS = 10

INFOS = [0.1]

server = FlaskAPI(__name__)

@server.route("/", methods=['GET'])
def function():
    global INFOS
    avg_data = np.mean(INFOS) # get average 
    INFOS = [INFOS[-1]] # reset the data
    return {'data':avg_data}, status.HTTP_200_OK

def start_rest_api():
    server.run(host=HOST,port=REST_PORT)
    print('completed!')

def background_retrieve_fps(server):
    global STREAM_FPS
    command = 'ffmpeg  -i ' + server + ' -f null -'
    print(command)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)

    # for line in process.stdout:
    #     print(line)

    while True:
        fps = 10 # default
        outputs = process.stdout.readline().split() 
        idx_fps, idx_speed, idx_bitrate = -1, -1, -1

        for i, out in enumerate(outputs):
            if out.find('fps')!=-1:
                idx_fps = i
            if out.find('speed')!=-1:
                idx_speed = i
            if out.find('bitrate')!=-1:
                idx_bitrate = i

        if idx_bitrate!= -1:
            try:
                print(float(outputs[idx_bitrate+1].split('=')[-1]))
            except: pass

        if idx_fps!=-1 and idx_speed!=-1:
            try:
                STREAM_FPS = float(outputs[idx_fps + 1]) / float(outputs[idx_speed].split('=')[-1].split('x')[0])
            except:
                pass


t1 = threading.Thread(target = background_retrieve_fps, args=(rtmp_server,))
t1.setDaemon(True)
t1.start()

# start rest api server
t2 = threading.Thread(target = start_rest_api)
t2.setDaemon(True)
t2.start()

while True:
    time.sleep(1)
    print(STREAM_FPS)






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
