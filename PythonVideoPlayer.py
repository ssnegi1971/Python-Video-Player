# pip install python-vlc
# download and install video player from : https://videolan.org
# video download: https://pexels.com
import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk

vlc_path = r'C:\Program Files\VideoLAN\VLC'
if os.path.exists(vlc_path):
  os.add_dll_directory(vlc_path)

import vlc


class VideoPlayerApp(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title('Python Media Player (AVI / MP4 / MKV)')
    self.geometry('800x600')

    # Disable hardware acceleration (--avcodec-hw=none) to fix Intel UHD D3D11VA buffer errors
    # Add '--quiet' to suppress non-fatal Windows child-window thumbnail warnings
    self.instance = vlc.Instance('--avcodec-hw=none', '--quiet')
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

    # Volume control
    tk.Label(control_panel, text='Volume:').pack(side=tk.LEFT, padx=(15, 5))
    self.volume_var = tk.IntVar(value=80)
    self.volume_slider = ttk.Scale(
        control_panel,
        from_=0,
        to=100,
        orient=tk.HORIZONTAL,
        variable=self.volume_var,
        command=self.set_volume,
    )
    self.volume_slider.pack(side=tk.LEFT, padx=5)
    self.media_player.audio_set_volume(80)

    # Ensure window is drawn before attaching VLC video output
    self.update_idletasks()
    self._bind_video_window()

    # Start periodic UI update loop for timeline
    self.update_timeline()

  def _bind_video_window(self):
    """Attach VLC video output to the Tkinter frame across platforms."""
    win_id = self.video_frame.winfo_id()
    if sys.platform.startswith('win'):
      self.media_player.set_hwnd(win_id)
    elif sys.platform == 'darwin':
      self.media_player.set_nsobject(win_id)
    else:
      self.media_player.set_xwindow(win_id)

  def open_file(self):
    file_path = filedialog.askopenfilename(
        title='Select a Video File',
        filetypes=(
            ('Video Files', '*.mp4 *.avi *.mkv *.mov *.wmv'),
            ('All Files', '*.*'),
        ),
    )
    if file_path:
      media = self.instance.media_new(file_path)
      self.media_player.set_media(media)
      self._bind_video_window()
      self.play_video()

  def play_video(self):
    if self.media_player.get_media():
      self.media_player.play()

  def pause_video(self):
    self.media_player.pause()

  def stop_video(self):
    self.media_player.stop()
    self.seek_var.set(0)
    self.time_label.config(text='00:00 / 00:00')

  def set_volume(self, value):
    self.media_player.audio_set_volume(int(float(value)))

  def on_slider_press(self, event):
    self.is_dragging = True

  def on_slider_release(self, event):
    self.is_dragging = False
    self.on_seek(self.seek_var.get())

  def on_seek(self, value):
    if self.is_dragging and self.media_player.get_length() > 0:
      pos = float(value) / 1000.0
      self.media_player.set_position(pos)

  def format_time(self, milliseconds):
    if milliseconds < 0:
      return '00:00'
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
      return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    return f'{minutes:02d}:{seconds:02d}'

  def update_timeline(self):
    if self.media_player.is_playing() and not self.is_dragging:
      length = self.media_player.get_length()
      current = self.media_player.get_time()
      if length > 0:
        pos = (current / length) * 1000
        self.seek_var.set(pos)
        self.time_label.config(
            text=f'{self.format_time(current)} / {self.format_time(length)}'
        )
    self.after(500, self.update_timeline)

  def on_closing(self):
    self.media_player.stop()
    self.destroy()


if __name__ == '__main__':
  app = VideoPlayerApp()
  app.protocol('WM_DELETE_WINDOW', app.on_closing)
  app.mainloop()
