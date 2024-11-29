import sys
import os
import time
import subprocess
from tkinter import DoubleVar, LEFT, RIGHT
from customtkinter import CTk, set_appearance_mode, set_default_color_theme, CTkSlider, \
    HORIZONTAL, CTkFrame, X, CTkLabel, CTkButton, CTkToplevel
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import vlc
import psutil

def get_desktop_path():
    """Get the path to the user's Desktop folder."""
    return os.path.join(os.path.expanduser("~"), "Desktop")

class WhiteRabbitPlayer(CTkToplevel):

    def __init__(self, *args, main_win, **kwargs):
        super().__init__(*args, **kwargs)

        # ============ WINDOW CONFIG ====================
        set_appearance_mode("dark")  # Modes: system (default), light, dark
        set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green
        self.geometry("420x81")
        self.resizable(False, False)
        self.configure(fg_color="#282829")
        self.version = "4.1"
        self.title(f"White Rabbit {self.version}")
        self.main_win = main_win

        # variables
        self.base_dir = os.path.dirname(__file__)
        self.audio_title = None
        self.audio_path = sys.argv[1] if len(sys.argv) > 1 else ''

        if self.audio_path and os.path.exists(self.audio_path):
            self.audio_title = os.path.basename(self.audio_path)
            
        self.playing_time_interval = None
        self.player = None
        self.slider = DoubleVar(value=0)
        self.volume = DoubleVar(value=50)
        self.AUDIO_EXTENSIONS = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']
        self.interval = CTkLabel(self)
        self.audio_path_update = CTkLabel(self)
        # self.audio_path_update.after(1, self.audio_path_checker)

        if not self.audio_path:
            print(self.audio_path)
            self.audio_error = CTkLabel(self,
                                        text=f"No Audio Selected. Please select an audio using the command :\n ./play_audio.sh <audio_path>.",
                                        font=("Roboto", 11),
                                        text_color="white",
                                        )
            self.audio_error.place(relx=.5, rely=.5, anchor="center")
            return

        # initialize python vlc
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Create Widgets
        self.create_audio_title()
        self.create_slider_frame()
        self.create_buttons_frame()
        self.create_volume_frame()
        self.set_audio_duration()
        self.playing_update()

        # play audio
        self.media = self.instance.media_new(self.audio_path)
        self.player.set_media(self.media)
        self.player.play()
        print(f"Playing audio: {self.audio_path}")
        self.change_frames_color("#C21807")

        self.protocol("WM_DELETE_WINDOW", self.on_closed)

    def is_audio_file(self, file_path):
        """Check if the given file has an audio file extension."""
        ext = os.path.splitext(file_path)[1]
        return ext.lower() in self.AUDIO_EXTENSIONS
    

    def on_closed(self):
        self.player.stop()
        print("Application closed.")
        self.quit()
        self.destroy()

    def playing_update(self):
        if True:
            self.current_time = self.player.get_time() / 1000
            self.slider.set(self.current_time)
            dot_index = str(self.current_time).find(".")
            milli = str(self.current_time)[dot_index + 1:]

            self.converted_current_time = time.strftime('%M:%S', time.gmtime(self.slider.get()))
            if len(milli) == 1:
                self.playing_time.configure(text=f"{self.converted_current_time}:{milli}00")
            elif len(milli) == 2:
                self.playing_time.configure(text=f"{self.converted_current_time}:{milli}0")
            else:
                self.playing_time.configure(text=f"{self.converted_current_time}:{milli}")

            self.playing_time_interval = self.interval.after(1, self.playing_update)

    def stop_playing_update(self):
        try:
            self.interval.after_cancel(self.playing_time_interval)
        except Exception as e:
            print(f"Error stopping playing update: {e}")

    def volume_slider_click(self, value):
        self.player.audio_set_volume(int(value))
        self.volume.set(int(value))
        print(f"Volume set to: {int(value)}")

    def playing_slider_click(self, value):
        round_value = round(value, 3)
        new_playing_time = int(value) * 1000
        self.slider.set(round_value)
        self.player.set_time(new_playing_time)
        print(f"Playing time set to: {new_playing_time} ms")

    def set_audio_duration(self):
        try:
            if self.audio_path.lower().endswith('.mp3'):
                song_mut = MP3(self.audio_path)
                song_length = song_mut.info.length
            elif self.audio_path.lower().endswith('.m4a'):
                song_mut = MP4(self.audio_path)
                song_length = song_mut.info.length
            else:
                raise ValueError("Unsupported audio format")

            converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
            self.playing_duration.configure(text=f"{converted_song_length}:00")
            self.playing_slider.configure(to=int(song_length))
            print(f"Audio duration set: {converted_song_length}")
        except Exception as e:
            print(f"Error setting audio duration: {e}")

    def pause_audio(self):
        self.change_frames_color("#282829")
        if self.player.get_time() > 0:
            self.player.set_pause(1)
            self.play_btn.configure(fg_color="#282829")
            self.pause_btn.configure(fg_color="#022861")
            self.replay_btn.configure(fg_color="#282829")
            print("Audio paused.")
            self.stop_playing_update()

    def change_frames_color(self, color):
        self.slider_frame.configure(fg_color=color)
        self.audio_title_frame.configure(fg_color=color)
        self.volume_frame.configure(fg_color=color)
        self.buttons_frame.configure(fg_color=color)

    def play_audio(self):
        self.change_frames_color("#C21807")
        if not self.player.get_state() == vlc.State.Playing and not self.player.get_state() == vlc.State.Ended:
            if self.player.get_time() <= 0:
                self.player.play()
                print("Audio playing from start.")
            elif self.player.get_time() > 0:
                self.player.set_pause(0)
                print("Audio resumed playing.")

            self.playing_update()
            self.play_btn.configure(fg_color="#022861")
            self.pause_btn.configure(fg_color="#282829")
            self.replay_btn.configure(fg_color="#282829")
            
        if self.player.get_state() == vlc.State.Ended:
            print('replayying')
            self.replay_audio()

    def replay_audio(self):
        self.change_frames_color("#C21807")
        self.player.stop()
        self.stop_playing_update()
        self.player.play()
        self.play_btn.configure(fg_color="#282829")
        self.pause_btn.configure(fg_color="#282829")
        self.replay_btn.configure(fg_color="#022861")
        self.playing_update()

    def create_audio_title(self):
        self.audio_title_frame = CTkFrame(self, height=30, )
        self.audio_title_frame.pack(fill=X)

        self.audio_title_label = CTkLabel(self.audio_title_frame,
                                      text=f"{self.audio_title[:-4]}",
                                      font=("Roboto", 17, "bold"),
                                      text_color="white",
                                      )
        self.audio_title_label.place(relx=.5, rely=.5, anchor="center")

    def create_slider_frame(self):
        self.slider_frame = CTkFrame(self, height=20, )
        self.slider_frame.pack(fill=X)

        self.playing_time = CTkLabel(self.slider_frame,
                                     text="00:00:00",
                                     font=("Roboto", 15),
                                     text_color="white",
                                     )
        self.playing_time.place(relx=.03, rely=.5, anchor="w")

        self.playing_slider = CTkSlider(self.slider_frame,
                                        from_=0,
                                        to=100,
                                        orientation=HORIZONTAL,
                                        fg_color="white",
                                        progress_color="#42daf5",
                                        variable=self.slider,
                                        command=self.playing_slider_click,
                                        width=240)
        self.playing_slider.place(relx=.5, rely=.5, anchor="center")

        self.playing_duration = CTkLabel(self.slider_frame,
                                         text="05:00",
                                         font=("Roboto", 15),
                                         text_color="white",
                                         )
        self.playing_duration.place(relx=.95, rely=.5, anchor="e")

    def create_buttons_frame(self):
        self.buttons_frame = CTkFrame(self, height=30, )
        self.buttons_frame.pack(fill=X, side=LEFT)

        self.play_btn = CTkButton(self.buttons_frame,
                                  text="Play",
                                  font=("Roboto", 14),
                                  width=50,
                                  height=20,
                                  fg_color="#022861",
                                  border_color='#006391',
                                  border_width=2,
                                  command=self.play_audio,
                                  )
        self.play_btn.place(relx=.15, rely=.5, anchor="center")

        self.pause_btn = CTkButton(self.buttons_frame,
                                   text="Pause",
                                   font=("Roboto", 14),
                                   width=50,
                                   height=20,
                                   fg_color="#282829",
                                   border_color='#006391',
                                   border_width=2,
                                   command=self.pause_audio
                                   )
        self.pause_btn.place(relx=.44, rely=.5, anchor="center")

        self.replay_btn = CTkButton(self.buttons_frame,
                                    text="Replay",
                                    font=("Roboto", 14),
                                    width=50,
                                    height=20,
                                    fg_color="#282829",
                                    border_color='#006391',
                                    border_width=2,
                                    command=self.replay_audio
                                    )
        self.replay_btn.place(relx=.75, rely=.5, anchor="center")

    def create_volume_frame(self):
        self.volume_frame = CTkFrame(self, height=30, width=300)
        self.volume_frame.pack(fill=X, side=RIGHT)

        # self.min_volume_label = CTkLabel(self.volume_frame,
        #                                  text="Vol -",
        #                                  )
        # self.min_volume_label.place(relx=.05, rely=.5, anchor="w")


        self.volume_slider = CTkSlider(self.volume_frame,
                                       from_=0,
                                       to=100,
                                       orientation=HORIZONTAL,
                                       command=self.volume_slider_click,
                                       progress_color="#f54242",
                                       width=120)
        self.volume_slider.place(relx=.7, rely=.5,
                                 anchor="center")
        
        self.volume_label = CTkLabel(self.volume_frame,
                                        #  text=f"{int(self.volume_slider.get())}%",
                                         textvariable=self.volume,
                                         )
        self.volume_label.place(relx=.33, rely=.5, anchor="w")
        

        self.volume_text_label = CTkLabel(self.volume_frame,
                                         text="Volume:",
                                         )
        self.volume_text_label.place(relx=.1, rely=.5, anchor="w")
        
class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x400")
        
        self.white_rabbit_app1 = None
        self.white_rabbit_app2 = None
        self.withdraw()
        
        self.start_white_rabbit()

            
    def start_white_rabbit(self):
        if self.white_rabbit_app1 is None or not self.white_rabbit_app1.winfo_exists():
            print(1)
            if self.white_rabbit_app2:
                if self.white_rabbit_app2.player:
                    self.white_rabbit_app2.player.stop()
                self.white_rabbit_app2.destroy()
                self.white_rabbit_app2 = None
                
            self.white_rabbit_app1 = WhiteRabbitPlayer(self, main_win=self)  
        else:
            print(2)
            if self.white_rabbit_app1:
                if self.white_rabbit_app1.player:
                    self.white_rabbit_app1.player.stop()
                self.white_rabbit_app1.destroy()
                self.white_rabbit_app1 = None

            self.white_rabbit_app2 = WhiteRabbitPlayer(self, main_win=self)  


if __name__ == '__main__':
    app = App()
    app.mainloop()
