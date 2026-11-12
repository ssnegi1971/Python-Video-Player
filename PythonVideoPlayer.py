# pip install python-vlc
# download and install video player from : https://www.videolan.org/vlc/
# video download: https://www.pexels.com/videos/
import os
import sys

vlc_path = r'C:\Program Files\VideoLAN\VLC'
if os.path.exists(vlc_path):
  os.add_dll_directory(vlc_path)

import tkinter as tk
from tkinter import filedialog, ttk
import vlc


class VideoPlayerApp(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title('Python Media Player (AVI / MP4 / MKV)')
    self.geometry('800x600')

    # Create VLC instance and player
    self.instance = vlc.Instance()
    self.media_player = self.instance.media_player_new()
    self.is_dragging = False

    # Video display panel
    self.video_frame = tk.Frame(self, bg='black')
    self.video_frame.pack(fill=tk.BOTH, expand=True)

    # Timeline / Seek bar frame
    timeline_panel = tk.Frame(self)
    timeline_panel.pack(fill=tk.X, padx=10, pady=(5, 0))

    self.time_label = tk.Label(timeline_panel, text='00:00 / 00:00')
    self.time_label.pack(side=tk.RIGHT, padx=5)

    self.seek_var = tk.DoubleVar()
    self.seek_slider = ttk.Scale(
        timeline_panel,
        from_=0,
        to=1000,
        orient=tk.HORIZONTAL,
        variable=self.seek_var,
        command=self.on_seek,
    )
    self.seek_slider.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=5)

    # Track mouse clicks so auto-update doesn't fight manual dragging
    self.seek_slider.bind('<ButtonPress-1>', self.on_slider_press)
    self.seek_slider.bind('<ButtonRelease-1>', self.on_slider_release)

    # Control buttons frame
    control_panel = tk.Frame(self)
    control_panel.pack(fill=tk.X, padx=10, pady=10)

    self.btn_open = tk.Button(
        control_panel, text='Open File', command=self.open_file
    )
    self.btn_open.pack(side=tk.LEFT, padx=5)

    self.btn_play = tk.Button(
        control_panel, text='Play', command=self.play_video
    )
    self.btn_play.pack(side=tk.LEFT, padx=5)

    self.btn_pause = tk.Button(
        control_panel, text='Pause', command=self.pause_video
    )
    self.btn_pause.pack(side=tk.LEFT, padx=5)

    self.btn_stop = tk.Button(
        control_panel, text='Stop', command=self.stop_video
    )
    self.btn_stop.pack(side=tk.LEFT, padx=5)

    # Start the periodic UI update loop
    self.update_timeline()

  def open_file(self):
    file_path = filedialog.askopenfilename(
        filetypes=[
            ('Video Files', '*.avi *.mp4 *.mkv *.mov *.webm'),
            ('All Files', '*.*'),
        ]
    )
    if file_path:
      media = self.instance.media_new(file_path)
      self.media_player.set_media(media)

      # Embed video window to Tkinter frame based on OS
      if sys.platform.startswith('linux'):
        self.media_player.set_xwindow(self.video_frame.winfo_id())
      elif sys.platform == 'win32':
        self.media_player.set_hwnd(self.video_frame.winfo_id())
      elif sys.platform == 'darwin':
        self.media_player.set_nsobject(self.video_frame.winfo_id())

      self.play_video()

  def play_video(self):
    self.media_player.play()

  def pause_video(self):
    self.media_player.pause()

  def stop_video(self):
    self.media_player.stop()
    self.seek_var.set(0)
    self.time_label.config(text='00:00 / 00:00')

  def on_slider_press(self, event):
    self.is_dragging = True

  def on_slider_release(self, event):
    self.is_dragging = False
    self.set_video_position()

  def on_seek(self, value):
    # Update video position live while dragging
    if self.is_dragging:
      self.set_video_position()

  def set_video_position(self):
    length = self.media_player.get_length()
    if length > 0:
      pos = self.seek_var.get() / 1000.0
      self.media_player.set_position(pos)

  def format_time(self, milliseconds):
    if milliseconds < 0:
      return '00:00'
    seconds = int(milliseconds / 1000)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
      return f'{hours:02d}:{mins:02d}:{secs:02d}'
    return f'{mins:02d}:{secs:02d}'

  def update_timeline(self):
    # Sync slider and timestamp with current playback every 250ms
    if not self.is_dragging and self.media_player.is_playing():
      length = self.media_player.get_length()
      current = self.media_player.get_time()
      if length > 0:
        pos = (current / length) * 1000
        self.seek_var.set(pos)
        self.time_label.config(
            text=f'{self.format_time(current)} / {self.format_time(length)}'
        )

    self.after(250, self.update_timeline)


if __name__ == '__main__':
  app = VideoPlayerApp()
  app.mainloop()
