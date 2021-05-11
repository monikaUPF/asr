import requests
import io
import wave
import pyaudio

def play_audio(wf:wave.Wave_read):

    CHUNK = 1024

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    data = wf.readframes(CHUNK)

    # play stream (3)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()

def do_speech2text_request(path:str):

    file_data = {'file': open(path,'rb')}
    req = requests.post("http://localhost:4200/speech2text", files=file_data)
    print(req.text)


if __name__ == "__main__":
    # do_text2speech_request("Hello!")
    do_speech2text_request("speech2text/audio_A.wav")