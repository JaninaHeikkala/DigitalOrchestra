# IMPORTS
import os
import sys

from config import *
import time
import numpy as np
from random import randrange, choice
import cv2
import imutils
from threading import Thread
from psonic import *
from PySide6 import QtCore, QtWidgets, QtGui
from multiprocessing import Process

# CONSTANTS
CAMERA_WIDTH = WEBCAM_WIDTH
CAMERA_HEIGHT = WEBCAM_HEIGHT

LOOP_PLAY_ON = loopPlayOn

currentFrame = None

# GET SONIC PI TOKEN TO BE ABLE TO PLAY SOUND (remember to start Sonic Pi before starting Digital Orchestra)
log_path = os.path.expanduser("~/.sonic-pi/log/spider.log")
set_server_parameter_from_log('127.0.0.1')
set_server_parameter_from_log('127.0.0.1', log_path)

# CONSTANT KICK IF drumKickOn = True
def drumKick(color):
    print("Drum Kick")
    while True:
        if color == "green": sample(BD_GAS)
        if color == "red" : sample(DRUM_HEAVY_KICK, amp=0.9)
        if color == "blue" : sample(BASS_HIT_C, amp= 0.3)
        sleep(1)

def ambient(color):
    print("Ambient")

    while True:
        if color == "green":
            c = choice([
                chord(C3, MAJOR7), # I
                chord(C3, MAJOR7), # I
                chord(G3, DOM7), # V
                chord(A3, MINOR7) # vi
            ])
            # c = chord(C3, MAJOR7)
            use_synth(HOLLOW)
            play(c, release=8)
            sleep(8)
        if color == "red":
            c = choice([
                chord(C3, MINOR7),  # i
                chord(Ab3, MAJOR7),  # VI
                chord(Bb3, DOM7),  # VII
                chord(F3, MINOR7) # iv
            ])
            # c = chord(C3, MINOR7)
            use_synth(TRI)
            play(c, release=8, amp=1)
            sleep(8)
        if color == "blue":
            c = chord(C3, MINOR7)
            use_synth(DARK_AMBIENCE)
            play(c, release=8, amp=2)
            sleep(8)


def get_scale(root, scale_type):
    """Get a scale based on the root and scale type"""
    scale_intervals = scalesIntervals.get(scale_type, scalesIntervals["minor"])  # Default to minor if invalid scale type
    scale_notes = []

    for interval in scale_intervals:
        note = root + interval  # Generate note based on the root and interval
        scale_notes.append(note)

    return scale_notes

def trackPoint(grayimage1, grayimage2):
    moveData = []  # initialize list of movementCenterPoints
    biggestArea = MIN_AREA
    # Get differences between the two greyed images
    differenceImage = cv2.absdiff(grayimage1, grayimage2)
    # Blur difference image to enhance motion vectors
    differenceImage = cv2.blur(differenceImage, (BLUR_SIZE, BLUR_SIZE))
    # Get threshold of blurred difference image based on THRESHOLD_SENSITIVITY variable
    retval, thresholdImage = cv2.threshold(differenceImage, thresHoldSensitivity, 255, cv2.THRESH_BINARY)
    try:
        thresholdImage, contours, hierarchy = cv2.findContours(thresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        contours, hierarchy = cv2.findContours(thresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours != ():
        for c in contours:
            cArea = cv2.contourArea(c)
            if cArea > biggestArea:
                biggestArea = cArea
                (x, y, w, h) = cv2.boundingRect(c)
                cx = int(x + w / 2)  # x center point of contour
                cy = int(y + h / 2)  # y center point of contour
                moveData = [cx, cy, w, h]
    return moveData

def playMusic(prevSynth, moveData, color, saveMelody, prevTime):
    currTime = time.time()
    delta = currTime - prevTime
    delta = round(delta, 2)
    print("current time: ", delta)

    # Get real webcam size (the constants seem to just give an aspect ratio? (scale))
    actual_width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Get contour data for movement position
    x, y, w, h = moveData[0], moveData[1], moveData[2], moveData[3]

    # divides the screen into zones for different notes and octaves
    # the highest octaves are played when there is movement at the top of the screen
    # the highest note in the octave is played when there is movement in the right part of the screen
    yZoneSize = actual_height / len(octavePicks)

    # select synth
    flip = random.randint(0, 1)
    if flip == 1:
        synthCur = random.choice([s for s in synthList if s[0] in synthPicks])
        prevSynth = synthCur
    else:
        synthCur = prevSynth

    synthName = synthCur[1]  # Get the synthName from synthCur
    use_synth(Synth(synthName))  # Activate the selected synthName

    # Determine the octave zone (y-axis) based on movement
    octaveCur = None  # Default in case no match is found

    for i in range(len(octavePicks)):
        if y < (i + 1) * yZoneSize:
            octaveCur = octaveList[octavePicks[i]]
            break
    octaveNotes = octaveCur[1]

    # Get the desired scale of the chosen octave
    if color == "green": scale = "major"
    else: scale = "minor"
    scale_notes = get_scale(octaveNotes[0], scale)
    xZoneSize = actual_width / len(scale_notes)  # how many notes in the chosen scale

    note = None

    for i in range(len(scale_notes)):
        if x < (i + 1) * xZoneSize:
            note = scale_notes[i]
            break

    amplitude = 0.01 + (0.3 - 0.01) * ((w + h) - 0) / (100 - 0)
    amplitude = max(0.01, min(0.3, amplitude))
    play(note, amp=amplitude)
    saveMelody.append([note, synthName, delta])
    sleep(noteSleep)

    if drumPlayOn:
        if w <= actual_width/10 and h <= actual_height/10:
            print("Drum Play", w, h)
            drum = drumList[drumPicks[randrange(len(drumPicks))]]
            sample(drum[1], amp=0.2)
            sleep(random.choice([0.25, 0.5, 0.33, 1])) # 0.25, 0.5, 0.33, 1

    return prevSynth, saveMelody, currTime


def digitalOrchestra(color):
    global startTime
    # global currentFrame

    while currentFrame is None:
        sleep(0.01)

    startTime = time.time()
    startTime = round(startTime, 2)
    prevTime = startTime

    loop = LOOP_PLAY_ON
    # image1 = image2
    grayImage1 = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2GRAY) # Using gray images to save resources
    still_scanning = True
    prevSynth = synthList[synthPicks[0]]
    # If loopPlayOn is True, a melody is saved and looped throughout the program
    saveNotesNum = random.choice([4, 8, 12, 16]) # How many notes are being saved to saveMelody
    saveMelody = []
    # saveMelodyRepeat = random.choice([4, 8, 12, 16]) # How many times saved melody is repeated

    while still_scanning:
        if currentFrame is None:
            continue

        grayImage2 = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2GRAY)
        moveData = trackPoint(grayImage1, grayImage2) # Detect movement by comparing current frame with previous frame
        grayImage1 = grayImage2

        # Movement detected
        if moveData:
            print("movement found", moveData)
            prevSynth, saveMelody, currTime = playMusic(prevSynth, moveData, color, saveMelody, prevTime)
            prevTime = currTime

        if loop == False & len(saveMelody) == saveNotesNum & LOOP_PLAY_ON:
            loop = LOOP_PLAY_ON

        if loop:
            if len(saveMelody) == saveNotesNum:
                print("playing saved melody", saveMelody)
                for i in range(saveNotesNum):
                    use_synth(Synth(saveMelody[i][1]))
                    play(saveMelody[i][0], amp=0.5)
                    sleep(saveMelody[i][2])
                # reset the saved melody
                saveNotesNum = random.choice([4, 8, 12, 16])
                saveMelody = []
                # saveMelodyRepeat = random.choice([4, 8, 12, 16])
                loop = False
                prevTime = time.time()
                prevTime = round(prevTime, 2)

def startApp():
    global synthPicks
    global drumPicks
    global currentFrame
    global drumKickOn, ambientOn
    global vid

    try:
        vid = cv2.VideoCapture(0)

        if not vid.isOpened():
            print("Error: Could not open webcam")
            return

        cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

        vid.set(3, WEBCAM_WIDTH)
        vid.set(4, WEBCAM_HEIGHT)

        rect, frame = vid.read()
        cv2.imshow('frame', frame)

        # setting values for base colors
        b = frame[:, :, 0]  # Blue channel
        g = frame[:, :, 1]  # Green channel
        r = frame[:, :, 2]  # Red channel

        # computing the mean
        b_mean = np.mean(b)
        g_mean = np.mean(g)
        r_mean = np.mean(r)

        # displaying the most prominent color
        if b_mean > g_mean and b_mean > r_mean:
            print("Blue")
            color = "blue"
            synthPicks = blueSynthPicks
            drumPicks = blueDrumPicks
        elif g_mean > r_mean and g_mean > b_mean:
            print("Green")
            color = "green"
            synthPicks = greenSynthPicks
            drumPicks = greenDrumPicks
        else:
            print("Red")
            color = "red"
            synthPicks = redSynthPicks
            drumPicks = redDrumPicks

        orchestra_thread = Thread(
            target=digitalOrchestra,
            args=(color,),
            daemon=True
        )
        orchestra_thread.start()

        while True:

            ret, frame = vid.read()
            if not ret:
                continue

            currentFrame = frame
            cv2.imshow('frame', frame)

            if drumKickOn:
                kickThread = Thread(target=drumKick, args=(color,), daemon=True)
                kickThread.start()
                drumKickOn = False  # Prevents multiple drum kick threads from starting

            if ambientOn:
                ambientThread = Thread(target=ambient, args=(color,), daemon=True)
                ambientThread.start()
                ambientOn = False

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
                break

    except KeyboardInterrupt:
        print("-------------------------")
        print("Exiting digital orchestra")
        print("-------------------------")
        quit(0)
    finally:
        if 'vid' in locals() and vid is not None:
            vid.release()
        cv2.destroyAllWindows()

def startAppFromUI():
    # Collect values from the UI widget and update globals
    global widget
    
    try:
        # Get values from UI inputs
        width = int(widget.widthInput.text()) if widget.widthInput.text() else WEBCAM_WIDTH
        height = int(widget.heightInput.text()) if widget.heightInput.text() else WEBCAM_HEIGHT
        note_sleep = float(widget.noteSleepInput.text()) if widget.noteSleepInput.text() else noteSleep
        threshold = int(widget.thresholdInput.text()) if widget.thresholdInput.text() else thresHoldSensitivity
        
        loop_play = widget.loopPlayDropdown.currentText() == "True"
        drum_play = widget.drumPlayDropdown.currentText() == "True"
        drum_kick = widget.drumKickDropdown.currentText() == "True"
        ambient = widget.ambientDropdown.currentText() == "True"
        
    except ValueError:
        print("Invalid input values")
        return
    
    # Update global variables
    globals()['WEBCAM_WIDTH'] = width
    globals()['CAMERA_WIDTH'] = width
    globals()['WEBCAM_HEIGHT'] = height
    globals()['CAMERA_HEIGHT'] = height
    globals()['noteSleep'] = note_sleep
    globals()['thresHoldSensitivity'] = threshold
    globals()['LOOP_PLAY_ON'] = loop_play
    globals()['loopPlayOn'] = loop_play
    globals()['drumPlayOn'] = drum_play
    globals()['drumKickOn'] = drum_kick
    globals()['ambientOn'] = ambient
    
    # Update config.py file
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    try:
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Replace config values
        config_content = _update_config_value(config_content, 'WEBCAM_WIDTH', str(width))
        config_content = _update_config_value(config_content, 'WEBCAM_HEIGHT', str(height))
        config_content = _update_config_value(config_content, 'noteSleep', str(note_sleep))
        config_content = _update_config_value(config_content, 'thresHoldSensitivity', str(threshold))
        config_content = _update_config_value(config_content, 'loopPlayOn', str(loop_play))
        config_content = _update_config_value(config_content, 'drumPlayOn', str(drum_play))
        config_content = _update_config_value(config_content, 'drumKickOn', str(drum_kick))
        config_content = _update_config_value(config_content, 'ambientOn', str(ambient))
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("Config file updated successfully")
    except Exception as e:
        print(f"Error updating config file: {e}")
    
    # root.destroy()
    p = Process(target=startApp)
    p.start()
    # Thread(target=startApp, daemon=True).start()

def _update_config_value(content, key, value):
    """Helper function to update a config value in the content string"""
    import re
    
    # Handle different types of values
    if value.lower() in ['true', 'false']:
        # Boolean values
        pattern = rf"({key}\s*=\s*)(True|False)"
        return re.sub(pattern, lambda m: m.group(1) + value, content)
    else:
        # Numeric or string values
        try:
            # Try to convert to float to check if it's a number
            float(value)
            pattern = rf"({key}\s*=\s*)[\d.]+"
            return re.sub(pattern, lambda m: m.group(1) + value, content)
        except ValueError:
            # String value
            pattern = rf"({key}\s*=\s*)(['\"].*?['\"]|[\w]+)"
            return re.sub(pattern, lambda m: m.group(1) + '"' + value + '"', content)

'''
def clearWindow():
    global container
    container.destroy()

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)
    


def showMainMenu():

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20, fill="both", expand=True)


    # Buttons
    tk.Button(frame, text="Start creating music!", command=startAppFromUI).pack(pady=10)

    # Entries with labels
    tk.Label(frame, text="Width").pack(pady=2)
    width_entry = tk.Entry(root)
    width_entry.insert(0, WEBCAM_WIDTH)
    width_entry.pack(pady=5)

    tk.Label(frame, text="Height").pack(pady=2)
    height_entry = tk.Entry(root)
    height_entry.insert(0, WEBCAM_HEIGHT)
    height_entry.pack(pady=5)

    tk.Label(frame, text="First Name").pack(pady=5)

    tk.Button(frame, text="Start playing!").pack(pady=5)
    '''


class DigOrchWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.appProcess = None

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        # Create button layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setSpacing(10)
        
        self.buttonStart = QtWidgets.QPushButton("Start creating music!")
        self.buttonStart.setMaximumWidth(200)
        self.buttonStart.clicked.connect(self.startApp)
        buttonLayout.addWidget(self.buttonStart)
        
        self.buttonSave = QtWidgets.QPushButton("Save Settings")
        self.buttonSave.setMaximumWidth(200)
        self.buttonSave.clicked.connect(self.saveSettings)
        buttonLayout.addWidget(self.buttonSave)

        self.buttonExit = QtWidgets.QPushButton("Exit")
        self.buttonExit.setMaximumWidth(200)
        self.buttonExit.clicked.connect(self.exitApplication)
        buttonLayout.addWidget(self.buttonExit)
        
        buttonLayout.addStretch()
        self.layout.addLayout(buttonLayout)

        # Create a grid layout for settings
        settingsLayout = QtWidgets.QGridLayout()
        settingsLayout.setSpacing(10)
        settingsLayout.setColumnStretch(0, 0)  # Label column
        settingsLayout.setColumnStretch(1, 1)  # Input column

        self.layout.addSpacing(30)

        # Row 0: Webcam width
        self.labelWidth = QtWidgets.QLabel("Webcam width:")
        self.labelWidth.setToolTip("Set the width of the webcam input in pixels. Default: 320")
        self.widthInput = QtWidgets.QLineEdit(self, placeholderText=str(WEBCAM_WIDTH))
        self.widthInput.setValidator(QtGui.QIntValidator())
        self.widthInput.setMaximumWidth(200)
        self.widthInput.setToolTip("Set the width of the webcam input in pixels. Default: 320")
        settingsLayout.addWidget(self.labelWidth, 0, 0)
        settingsLayout.addWidget(self.widthInput, 0, 1)

        # Row 1: Webcam height
        self.labelHeight = QtWidgets.QLabel("Webcam height:")
        self.labelHeight.setToolTip("Set the height of the webcam input in pixels. Default: 240")
        self.heightInput = QtWidgets.QLineEdit(self, placeholderText=str(WEBCAM_HEIGHT))
        self.heightInput.setValidator(QtGui.QIntValidator())
        self.heightInput.setMaximumWidth(200)
        self.heightInput.setToolTip("Set the height of the webcam input in pixels. Default: 240")
        settingsLayout.addWidget(self.labelHeight, 1, 0)
        settingsLayout.addWidget(self.heightInput, 1, 1)

        # Row 2: Note sleep
        self.labelNoteSleep = QtWidgets.QLabel("Note sleep:")
        self.labelNoteSleep.setToolTip("Set the delay (in seconds) between note triggers during motion detection. Default: 0.05")
        self.noteSleepInput = QtWidgets.QLineEdit(self, placeholderText=str(noteSleep))
        self.noteSleepInput.setValidator(QtGui.QDoubleValidator())
        self.noteSleepInput.setMaximumWidth(200)
        self.noteSleepInput.setToolTip("Set the delay (in seconds) between note triggers during motion detection. Default: 0.05")
        settingsLayout.addWidget(self.labelNoteSleep, 2, 0)
        settingsLayout.addWidget(self.noteSleepInput, 2, 1)

        # Row 3: Threshold sensitivity
        self.labelThreshold = QtWidgets.QLabel("Threshold sensitivity:")
        self.labelThreshold.setToolTip("Set the sensitivity threshold for motion detection. Lower values are more sensitive. Default: 80")
        self.thresholdInput = QtWidgets.QLineEdit(self, placeholderText=str(thresHoldSensitivity))
        self.thresholdInput.setValidator(QtGui.QIntValidator())
        self.thresholdInput.setMaximumWidth(200)
        self.thresholdInput.setToolTip("Set the sensitivity threshold for motion detection. Lower values are more sensitive. Default: 80")
        settingsLayout.addWidget(self.labelThreshold, 3, 0)
        settingsLayout.addWidget(self.thresholdInput, 3, 1)

        # Row 4: Loop play on
        self.labelLoopPlay = QtWidgets.QLabel("Loop play on:")
        self.labelLoopPlay.setToolTip("Enable or disable playback of looped saved melodies")
        self.loopPlayDropdown = QtWidgets.QComboBox()
        self.loopPlayDropdown.addItems(["True", "False"])
        self.loopPlayDropdown.setCurrentText("True" if LOOP_PLAY_ON else "False")
        self.loopPlayDropdown.setMaximumWidth(200)
        self.loopPlayDropdown.setToolTip("Enable or disable playback of looped saved melodies")
        settingsLayout.addWidget(self.labelLoopPlay, 4, 0)
        settingsLayout.addWidget(self.loopPlayDropdown, 4, 1)

        # Row 5: Drum play on
        self.labelDrumPlay = QtWidgets.QLabel("Drum play on:")
        self.labelDrumPlay.setToolTip("Enable or disable drum motion play")
        self.drumPlayDropdown = QtWidgets.QComboBox()
        self.drumPlayDropdown.addItems(["True", "False"])
        self.drumPlayDropdown.setCurrentText("True" if drumPlayOn else "False")
        self.drumPlayDropdown.setMaximumWidth(200)
        self.drumPlayDropdown.setToolTip("Enable or disable drum motion play")
        settingsLayout.addWidget(self.labelDrumPlay, 5, 0)
        settingsLayout.addWidget(self.drumPlayDropdown, 5, 1)

        # Row 6: Drum kick on
        self.labelDrumKick = QtWidgets.QLabel("Drum kick on:")
        self.labelDrumKick.setToolTip("Enable or disable the kick drum thread")
        self.drumKickDropdown = QtWidgets.QComboBox()
        self.drumKickDropdown.addItems(["True", "False"])
        self.drumKickDropdown.setCurrentText("True" if drumKickOn else "False")
        self.drumKickDropdown.setMaximumWidth(200)
        self.drumKickDropdown.setToolTip("Enable or disable the kick drum thread")
        settingsLayout.addWidget(self.labelDrumKick, 6, 0)
        settingsLayout.addWidget(self.drumKickDropdown, 6, 1)

        # Row 7: Ambient on
        self.labelAmbient = QtWidgets.QLabel("Ambient on:")
        self.labelAmbient.setToolTip("Enable or disable ambient background chords")
        self.ambientDropdown = QtWidgets.QComboBox()
        self.ambientDropdown.addItems(["True", "False"])
        self.ambientDropdown.setCurrentText("True" if ambientOn else "False")
        self.ambientDropdown.setMaximumWidth(200)
        self.ambientDropdown.setToolTip("Enable or disable ambient background chords")
        settingsLayout.addWidget(self.labelAmbient, 7, 0)
        settingsLayout.addWidget(self.ambientDropdown, 7, 1)

        self.layout.addLayout(settingsLayout)
        self.layout.addStretch()

    def getUIValues(self):
        try:
            width = int(self.widthInput.text()) if self.widthInput.text() else WEBCAM_WIDTH
            height = int(self.heightInput.text()) if self.heightInput.text() else WEBCAM_HEIGHT
            note_sleep = float(self.noteSleepInput.text()) if self.noteSleepInput.text() else noteSleep
            threshold = int(self.thresholdInput.text()) if self.thresholdInput.text() else thresHoldSensitivity
            
            loop_play = self.loopPlayDropdown.currentText() == "True"
            drum_play = self.drumPlayDropdown.currentText() == "True"
            drum_kick = self.drumKickDropdown.currentText() == "True"
            ambient = self.ambientDropdown.currentText() == "True"
            
            return {
                'width': width,
                'height': height,
                'note_sleep': note_sleep,
                'threshold': threshold,
                'loop_play': loop_play,
                'drum_play': drum_play,
                'drum_kick': drum_kick,
                'ambient': ambient
            }
        except ValueError:
            print("Invalid input values")
            return None

    def updateGlobals(self, values):
        """Update global variables with the given values"""
        globals()['WEBCAM_WIDTH'] = values['width']
        globals()['CAMERA_WIDTH'] = values['width']
        globals()['WEBCAM_HEIGHT'] = values['height']
        globals()['CAMERA_HEIGHT'] = values['height']
        globals()['noteSleep'] = values['note_sleep']
        globals()['thresHoldSensitivity'] = values['threshold']
        globals()['LOOP_PLAY_ON'] = values['loop_play']
        globals()['loopPlayOn'] = values['loop_play']
        globals()['drumPlayOn'] = values['drum_play']
        globals()['drumKickOn'] = values['drum_kick']
        globals()['ambientOn'] = values['ambient']

    def saveSettings(self):
        values = self.getUIValues()
        if values is None:
            return
        
        config_path = os.path.join(os.path.dirname(__file__), 'config.py')
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Replace config values
            config_content = _update_config_value(config_content, 'WEBCAM_WIDTH', str(values['width']))
            config_content = _update_config_value(config_content, 'WEBCAM_HEIGHT', str(values['height']))
            config_content = _update_config_value(config_content, 'noteSleep', str(values['note_sleep']))
            config_content = _update_config_value(config_content, 'thresHoldSensitivity', str(values['threshold']))
            config_content = _update_config_value(config_content, 'loopPlayOn', str(values['loop_play']))
            config_content = _update_config_value(config_content, 'drumPlayOn', str(values['drum_play']))
            config_content = _update_config_value(config_content, 'drumKickOn', str(values['drum_kick']))
            config_content = _update_config_value(config_content, 'ambientOn', str(values['ambient']))
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            print("Settings saved to config.py")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def startApp(self):
        values = self.getUIValues()
        if values is None:
            return
        
        self.updateGlobals(values)
        
        if self.appProcess is None or not self.appProcess.is_alive():
            self.appProcess = Process(target=startApp)
            self.appProcess.start()

    def _stopAppProcess(self):
        if self.appProcess is not None and self.appProcess.is_alive():
            self.appProcess.terminate()
            self.appProcess.join(timeout=2)
        self.appProcess = None

    def exitApplication(self):
        self._stopAppProcess()
        QtWidgets.QApplication.instance().quit()

    def closeEvent(self, event):
        self._stopAppProcess()
        super().closeEvent(event)


if __name__ == "__main__":
    global root

    app = QtWidgets.QApplication([])

    widget = DigOrchWidget()
    widget.resize(WEBCAM_WIDTH*2, WEBCAM_HEIGHT*2)
    widget.show()

    # showMainMenu()

    sys.exit(app.exec())
