import subprocess
import sys
import os
import torch
from transformers import AutoTokenizer
from llama_cpp import Llama
import whisper

def check_dependencies():
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
    try:
        model = whisper.load_model("base")
        return model.transcribe(file_path)["text"]
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)


# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = Llama(
  model_path="./mistral-7b-instruct-v0.2.Q4_K_M.gguf",  # Download the model file first
  n_ctx=32768,  # The max sequence len
  n_threads=8,  # The number of CPU threads to use, tweak to your system and the resulting performance
  n_gpu_layers=35 # The number of layers to offload to GPU
)

def analyze_and_summarize(text, llm):
    prompt = f"<s>[INST] You are tasked with creating concise meeting notes from transcribed audio. For each distinct topic discussed in the meeting, summarize it into a paragraph as a topic covered. Include an overview, key points, decisions, and action items related to that topic. Omit any small talk or non-essential discussions from the summary, such as conversations about the weather or personal matters not relevant to the meeting's objectives. Focus solely on the core topics and actionable insights. Transcript: {text} [/INST]</s>"

    # Using the __call__ method for inference from the example at https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
    output = llm(
        prompt,
        max_tokens=32768,  
        stop=["</s>"],
        echo=False       
    )

    # Extract the text part from the output
    if isinstance(output, dict) and 'choices' in output:
        response = output['choices'][0]['text'] if output['choices'] else "No response generated."
    else:
        response = str(output)  # Convert to string if output is not in the expected format


    # Writing the response to 'summary.txt'
    with open('summary.txt', 'w') as file:
        file.write(response)

    return response

def main():
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

    # Set device to use Apple Metal for GPU acceleration on macOS
    device = "mps" if torch.backends.mps.is_available() else "cpu"

    # Check if the model file exists
    model_path = "./mistral-7b-instruct-v0.2.Q4_K_M.gguf"  # Adjust model file path as needed
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}.")
        print("Please download the model file before proceeding.")
        print("Use the following command to download the model file:")
        print(f"huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF {model_path} --local-dir . --local-dir-use-symlinks False")
        sys.exit(1)

    # Initialize the Mistral 7B Instruct v0.2 model
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
