import speech_recognition as sr
from rapidfuzz import fuzz, process
import os
import pandas as pd
import whisper
from unidecode import unidecode
import paths
import re

MODEL = whisper.load_model("base")

def stt_openai(file_path, model):
    try:
        result = model.transcribe(file_path)
        print(result['text'])
    except:
        print(f"Error")

def stt_google(file_path):
    recognizer = sr.Recognizer()

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

def recognize_speech_from_flac(file_path, model_type=None):
    if model_type is None:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(file_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return "nan"
        except sr.RequestError as e:
            print(f"Error with the API request: {e}")
            return "nan"
        except:
            return "nan"
    else:
        try:
            result = model_type.transcribe(file_path)
            if 'text' in result:
                # Remove punctuation from the Whisper transcribed text
                text = re.sub(r'[^\w\s]', '', result['text'])
                return text
            else:
                return "nan"
        except:
            return "nan"

def process_flac_files_in_folder(folder_path, model_type=None):
    data = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".flac"):
            file_path = os.path.join(folder_path, file_name)
            
            transcribed_text = recognize_speech_from_flac(file_path, model_type)
            
            # Append the file name and transcription to the list
            if transcribed_text and transcribed_text != "nan":
                data.append([file_name.split('.')[0], transcribed_text])
            else:
                data.append([file_name.split('.')[0], "Transcription Failed"])

    df_flac = pd.DataFrame(data, columns=["file_name", "transcribed_text"])
    
    return df_flac

def compare_and_update_csv(flac_results_df, output_data_csv_path):
    df_output_data = pd.read_csv(output_data_csv_path)
    df_output_data["file_context"] = df_output_data["file_context"].apply(unidecode).str.lower()

    reference_contexts = list(df_output_data["file_context"].values)
    
    mapped_transcriptions = []
   
    # Filter out "Transcription Failed" and empty strings before comparison
    flac_results_df = flac_results_df[flac_results_df["transcribed_text"] != "Transcription Failed"]
    flac_results_df = flac_results_df[flac_results_df["transcribed_text"].str.strip() != ""]
    
    normalized_transcriptions = flac_results_df["transcribed_text"].apply(unidecode).str.lower().tolist()
    
    # Iterate and compare each transcription with reference contexts
    for transcription in normalized_transcriptions:
        if transcription and transcription.strip() != "":
            match, score, _ = process.extractOne(transcription, reference_contexts, scorer=fuzz.token_sort_ratio)
            mapped_transcriptions.append((transcription, match, score))
        else:
            mapped_transcriptions.append((transcription, None, 0))

    map_df = pd.DataFrame(mapped_transcriptions, columns=["Original", "Mapped", "Score"])
    
    flac_results_df["best_match"] = map_df["Mapped"]
    flac_results_df["similarity_score"] = map_df["Score"]
    flac_results_df["ai_output"] = map_df["Original"]
    
    merged_df = df_output_data.merge(flac_results_df, how="left", left_on="file_context", right_on="best_match")
    
    # Update the original DataFrame with the new similarity scores
    df_output_data["similarity_score"] = merged_df["similarity_score"]
    df_output_data["output"] = merged_df["ai_output"]
    
    df_output_data.to_csv(output_data_csv_path, index=False)
    
    print(f"output_data.csv updated successfully with similarity scores.")

if __name__ == "__main__":
    # audio_file = paths.SINGLE_VOICE_PATH
    # stt_google(audio_file)
    # stt_openai(audio_file, MODEL)

    flac_folder_path = paths.FLAC_FOLDER_PATH
    output_data_csv_path = paths.OUTPUT_DATA_CSV_PATH

    flac_results_df = process_flac_files_in_folder(flac_folder_path, model_type=MODEL)
    compare_and_update_csv(flac_results_df, output_data_csv_path)