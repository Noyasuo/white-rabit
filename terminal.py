import sys
import time
import subprocess
import threading
import os
import platform
import psutil

def play(audio_path):
    
    process_to_kill = "White Rabbit.exe"

    # get PID of the current process
    my_pid = os.getpid()

    # iterate through all running processes
    for p in psutil.process_iter():
        # if it's process we're looking for...
        if p.name() == process_to_kill:
            # and if the process has a different PID than the current process, kill it
            if not p.pid == my_pid:
                p.terminate()
        
    base_dir = os.path.dirname(__file__)
    input_text = os.path.join(base_dir, 'dist', 'White Rabbit', 'input_audio_to_play.txt')
    with open(input_text, 'w', encoding="utf-8") as data:
        data.write(audio_path)

    time.sleep(1)
    thread = threading.Thread(target=run_application)
    thread.start()

def run_application():
    white_rabbit_path = "C:\\Users\\Jomari\\projects\\amol\\white-rabbit-player\\dist\\White Rabbit\\White Rabbit.exe"

    try:
        if sys.platform.startswith('darwin'):
            # run on mac
            subprocess.run(['open', "C:\\Users\\Jomari\\projects\\amol\\white-rabbit-player\\dist\\White Rabbit\\White Rabbit.exe"], check=True)
        else:
            # run on windows
            subprocess.Popen([white_rabbit_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error executing the command:", e)

        

if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])