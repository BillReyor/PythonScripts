"""
This script is designed for transcribing audio files and generating concise summaries of the transcribed text. It first checks for necessary dependencies, including ffmpeg and Python packages like 'whisper' and 'transformers'. The script can transcribe audio files to text using the Whisper model. It then uses the Llama model (Mistral 7B Instruct version) to analyze and summarize the transcribed text, producing a concise summary of the key points and topics discussed in the audio.

Functions:
- check_dependencies(): Verifies the presence of required software and packages.
- transcribe_audio(file_path): Transcribes the audio from the given file path using the Whisper model.
- analyze_and_summarize(text, llm): Analyzes and summarizes the provided text using the Llama model.
- main(): Orchestrates the flow of the script from dependency checking, audio transcription, to text summarization.
"""

import subprocess
import sys
import os
import torch
from transformers import AutoTokenizer
from llama_cpp import Llama
import whisper

def check_dependencies():
    """
    Checks for the presence of required dependencies: ffmpeg and specific Python packages.
    Exits the script with an error message if a dependency is missing.
    """
    # Check for ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("ffmpeg is required. \nTo install ffmpeg:")
        print("  - On macOS: 'brew install ffmpeg'")
        sys.exit(1)

    # Check for Python packages
    try:
        import whisper
        from transformers import AutoModelForCausalLM
    except ImportError as e:
        missing_package = str(e).split("'")[1]
        print(f"Dependency missing: {missing_package}")
        if missing_package == 'whisper':
            print("To install, run: pip install git+https://github.com/openai/whisper.git")
        elif missing_package == 'transformers':
            print("To install, run: pip install transformers")
        else:
            print(f"To install, run: pip install {missing_package}")
        sys.exit(1)

def transcribe_audio(file_path):
    """
    Transcribes the audio from the specified file path using the Whisper model.

    Args:
    - file_path (str): Path to the audio file to be transcribed.

    Returns:
    - str: Transcribed text of the audio.

    Raises:
    - Exception: If any error occurs during transcription.
    """
    try:
        model = whisper.load_model("base")
        return model.transcribe(file_path)["text"]
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)

def analyze_and_summarize(text, llm):
    """
    Analyzes and summarizes the given text using the Llama model.

    Args:
    - text (str): Text to be summarized.
    - llm (Llama): Initialized Llama model.

    Returns:
    - str: Summarized text.

    The function constructs a specific prompt for the Llama model, sends the text for processing, and retrieves the summarized output. It also writes the summary to a text file.
    """
    prompt = f"<s>[INST] You are tasked with creating concise meeting notes from transcribed audio. For each distinct topic discussed in the meeting, summarize it into a paragraph as a topic covered. Include an overview, key points, decisions, and action items related to that topic. Omit any small talk or non-essential discussions from the summary, such as conversations about the weather or personal matters not relevant to the meeting's objectives. Focus solely on the core topics and actionable insights. Transcript: {text} [/INST]</s>"

    # Inference using the Llama model
    output = llm(
        prompt,
        max_tokens=32768,  
        stop=["</s>"],
        echo=False       
    )

    # Extracting text from the output
    if isinstance(output, dict) and 'choices' in output:
        response = output['choices'][0]['text'] if output['choices'] else "No response generated."
    else:
        response = str(output)  # Convert to string if not in expected format

    # Write summary to a file
    with open('summary.txt', 'w') as file:
        file.write(response)

    return response

def main():
    """
    Main function to orchestrate the script's operations.
    It involves checking dependencies, transcribing audio, and summarizing the transcription.
    """
    check_dependencies()
    file_path = input("Please enter the path to your MP3 audio file: ")
    transcription_file = file_path.rsplit('.', 1)[0] + '_transcription.txt'
    transcribed_text = ''
    if os.path.exists(transcription_file):
        use_existing = input(f"Transcription file {transcription_file} already exists. Use it (y/n)? ")
        if use_existing.lower() != 'y':
            transcribed_text = transcribe_audio(file_path)
            with open(transcription_file, 'w') as f:
                f.write(transcribed_text)
        else:
            with open(transcription_file, 'r') as f:
                transcribed_text = f.read()
    else:
        transcribed_text = transcribe_audio(file_path)
        with open(transcription_file, 'w') as f:
            f.write(transcribed_text)

    # GPU acceleration setup
    device = "mps" if torch.backends.mps.is_available() else "cpu"

    # Model file existence check
    model_path = "./mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}.")
        print("Please download the model file before proceeding.")
        print("Use the following command to download the model file:")
        print(f"huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF {model_path} --local-dir . --local-dir-use-symlinks False")
        sys.exit(1)

    # Initialize Llama model
    llm = Llama(
        model_path=model_path,
        n_ctx=32768,  # Max context window for the model
        n_threads=8,  # Number of CPU threads to use
        n_gpu_layers=35  # Number of layers to offload to GPU
    )

    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

    # Analyze and summarize the transcription
    summary = analyze_and_summarize(transcribed_text, llm)

    print("Summary:", summary)

if __name__ == "__main__":
    main()
