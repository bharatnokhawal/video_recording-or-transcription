import cv2
from datetime import datetime
import threading
import pyaudio
import wave
import speech_recognition as sr

cap = cv2.VideoCapture(0)
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
recordControl = 0
# recordControl = 0 : video is being captured (recorded)
# recordControl = 1 : video recording is paused
# recordControl = 2 : video recording is finished (to stop recording)
# we will record video and show current feed parallely using thread

class recordVideo(threading.Thread):  # thread class to record video
    def run(self):
        now = datetime.now()
        time = datetime.time(now)
        video_name = "capture_V_" + now.strftime("%y%m%d") + time.strftime("%H%M%S") + ".avi"
        audio_name = "audio_" + now.strftime("%y%m%d") + time.strftime("%H%M%S") + ".wav"

        # Video recording setup
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_name, fourcc, 16.0, (640, 480))

        # Audio recording setup
        audio_format = pyaudio.paInt16
        audio_channels = 1
        audio_sample_rate = 22050  
        audio_chunk = 1024  
        audio_record_seconds = 10  
        audio = pyaudio.PyAudio()

        stream = audio.open(format=audio_format,
                            channels=audio_channels,
                            rate=audio_sample_rate,
                            input=True,
                            frames_per_buffer=audio_chunk)

        frames = []

        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            if recordControl == 0:
                out.write(frame)

                # Audio recording
                audio_data = stream.read(audio_chunk)
                frames.append(audio_data)

            elif recordControl == 2:
                break

        out.release()
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save audio recording
        with wave.open(audio_name, 'wb') as wf:
            wf.setnchannels(audio_channels)
            wf.setsampwidth(audio.get_sample_size(audio_format))
            wf.setframerate(audio_sample_rate)
            wf.writeframes(b''.join(frames))

        # Transcribe the recorded audio
        transcribe_audio(audio_name)

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        transcription = recognizer.recognize_google(audio_data, language='en-US')
        print("Transcription:", transcription)
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def show_video():
    global recordControl
    m = 0  
    lock = False  
    while True:
        now = datetime.now()
        time = datetime.time(now)
        name = "capture_" + now.strftime("%y%m%d") + time.strftime("%H%M%S") + ".jpg"

        ret, frame = cap.read()
        if ret is True:
            frame = cv2.flip(frame, 1)   # 1 = vertical , 0 = horizontal

            cv2.imshow('frame', frame)

            k = cv2.waitKey(1) & 0Xff
            if k == ord('v'):  
                if lock is False:
                    recordControl = 0
                    m = m + 1
                    threadName = 'recordThread' + str(m)  
                    threadObj = recordVideo(name=threadName)
                    threadObj.start()
                    lock = True
            elif k == ord('q'):  # Quit program and recording
                if recordControl != 2:  
                    recordControl = 2
                threadObj.join()
                break
            elif k == ord('c'):  # capture Image
                cv2.imwrite(name, frame)
            elif k == ord('b'):  # stop recording
                recordControl = 2
                threadObj.join()
                lock = False
            elif k == ord('p'):  # pause recording
                recordControl = 1
            elif k == ord('r'):  # resume recording
                recordControl = 0
        else:
            break

if (cap.isOpened()):
    show_video()
else:
    cap.open()
    show_video()

cap.release()
cv2.destroyAllWindows()
