import speech_recognition as sr
import paths

def recognize_speech_from_file(file_path):
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Load audio file
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    # Recognize speech using Google Web Speech API
    try:
        text = recognizer.recognize_google(audio_data)
        print("Transcribed Text:")
        print(text)
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

if __name__ == "__main__":
    audio_file = paths.SINGLE_VOICE_PATH
    recognize_speech_from_file(audio_file)