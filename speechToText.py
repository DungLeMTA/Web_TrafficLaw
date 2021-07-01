import speech_recognition as sr
from gtts import gTTS
import playsound

# text = "Em nhà ở đâu thế"
# output = gTTS(text,lang="vi", slow=False)
# output.save("output.mp3")
# playsound.playsound('output.mp3', True)
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Mời bạn nói: ")
    audio = r.listen(source,phrase_time_limit=6)
    try:
        text = r.recognize_google(audio,language="vi-VI")
        print(text)
        output = gTTS(text, lang="vi", slow=False)
        output.save("output.mp3")
        playsound.playsound('output.mp3', True)
    except:
        print("Xin lỗi! tôi không nhận được voice!")






