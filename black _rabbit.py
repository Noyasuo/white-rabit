from customtkinter import CTk, set_appearance_mode, set_default_color_theme, CTkButton
from tkinter import filedialog
import os
import subprocess
import time
import multiprocessing
import threading
import sys
import psutil

class PlayerController(CTk):
    def __init__(self):
        super().__init__()

        set_appearance_mode("dark")  # Modes: system (default), light, dark
        set_default_color_theme("green")  # Themes: blue (default), dark-blue, green
        self.geometry("300x120")
        self.resizable(False, False)
        # self.configure(fg_color="#282829")
        self.title("Black Rabbit")
        self.eval('tk::PlaceWindow . center')
        self.app = None
        self.audio = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.path_audio1 = os.path.join(self.base_dir, 'love.mp3')
        self.audio1 = CTkButton(self,
                                text="Love of my life",
                                font=("fR{}oboto", 14),
                                width=50,
                                height=20,
                                fg_color="#022861",
                                border_color='#006391',
                                border_width=2,
                                command= lambda: self.play_audio(self.path_audio1),
                                )

        self.path_audio2 = os.path.join(self.base_dir, 'champions.mp3')
        self.audio2 = CTkButton(self,
                                text="We are the champions",
                                font=("Roboto", 14),
                                width=50,
                                height=20,
                                fg_color="#022861",
                                border_color='#006391',
                                border_width=2,
                                command= lambda: self.play_audio(self.path_audio2),
                                )

        self.path_audio3 = os.path.join(self.base_dir, 'bohemian.mp3')
        self.audio3 = CTkButton(self,
                                text="Bohemian Raphsody",
                                font=("Roboto", 14),
                                width=50,
                                height=20,
                                fg_color="#022861",
                                border_color='#006391',
                                border_width=2,
                                command= lambda: self.play_audio(self.path_audio3),
                                )
        

        self.audio1.place(relx=.5, rely=.2, anchor='center')
        self.audio2.place(relx=.5, rely=.5, anchor='center')
        self.audio3.place(relx=.5, rely=.8, anchor='center')

    def play_audio(self, audio_path):
        self.audio = audio_path
        time.sleep(1)
        thread = threading.Thread(target=self.run_application)
        thread.start()


    def run_application(self):
        process_to_kill = "White Rabbit"

        # get PID of the current process
        my_pid = os.getpid()

        # iterate through all running processes
        for p in psutil.process_iter():
            # if it's process we're looking for...
            if p.name() == process_to_kill:
                # and if the process has a different PID than the current process, kill it
                if not p.pid == my_pid:
                    p.terminate()

        # Replace "your_command_here" with the actual terminal command you want to run
        command_to_run = f"python white_rabbit.py play {self.audio}"

        try:
            # Run the command and capture its output
            output = subprocess.check_output(command_to_run, shell=True, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print(f"Command execution failed with error code: {e.returncode}")
        

if __name__ == '__main__':
    app = PlayerController()
    app.mainloop()
