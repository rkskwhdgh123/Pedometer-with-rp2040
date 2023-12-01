# raspberypi4
라즈베리파이4 수업
import speech_recognition as sr


r=sr.Recognizer()
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)
    print("please say anything...")
    audio=r.listen(source)
    try:
        print("you have said; \n"+r.recognize_google(audio))
    except Exception as e:
        print("Error: "+str(e))
