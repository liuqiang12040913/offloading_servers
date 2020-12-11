import subprocess
import string, time
import threading
import numpy as np
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

HOST = '0.0.0.0'
REST_PORT = 10002

rtmp_server = 'rtmp://'+HOST+'/LiveApp/1'

INFOS = [10]

server = FlaskAPI(__name__)

@server.route("/", methods=['GET'])
def function():
    global INFOS
    avg_data = np.mean(INFOS) # get average 
    INFOS = [INFOS[-1]] # reset the data
    return str(avg_data), status.HTTP_200_OK

def start_rest_api():
    server.run(host=HOST,port=REST_PORT)
    print('completed!')
   

if __name__ == "__main__":

    # start rest api server
    t1 = threading.Thread(target = start_rest_api)
    t1.setDaemon(True)
    t1.start()

    command = 'ffmpeg  -i ' + rtmp_server + ' -f null -'
    print(command)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # for line in process.stdout:
    #     print(line)

    while True:
        outputs = process.stdout.readline().split() # split command line output
        idx_fps, idx_speed, idx_bitrate = -1, -1, -1

        for i, out in enumerate(outputs):
            if out.find('fps') != -1:
                idx_fps = i
            if out.find('speed') != -1:
                idx_speed = i
            if out.find('bitrate') != -1:
                idx_bitrate = i

        if idx_bitrate!= -1: # in real, it does not have bitrate output
            try:
                print(float(outputs[idx_bitrate+1].split('=')[-1]))
            except: pass

        if idx_fps!=-1 and idx_speed!=-1: # if found fps, then append to INFOS
            try:
                INFOS.append( float(outputs[idx_fps + 1]) / float(outputs[idx_speed].split('=')[-1].split('x')[0]) )
            except:
                pass






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
