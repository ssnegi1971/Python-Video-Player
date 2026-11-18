Runs videos of type Python Media Player (AVI / MP4 / MKV)

#steps to create EXE for one-click use of app place PythonVideoPlayer.py in a folder (example:C:\Users\Admin\Desktop\work\Python\PythonApps) along with txt_studio.ico. #Goto command prompt

pip install pyinstaller

pyinstaller --noconsole --onefile --icon C:\Users\Admin\Desktop\work\Python\PythonApps\txt_studio.ico C:\Users\Admin\Desktop\work\Python\PythonApps\PythonVideoPlayer.py

It will create EXE in folder C:\Users\Admin\dist by default. Copy EXE to desired location.
