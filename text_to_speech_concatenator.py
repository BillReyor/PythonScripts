import openai
import os
from pydub import AudioSegment

def set_openai_api_key():
    """
    Sets the OpenAI API key by reading from the environment variable 'OPENAI_API_KEY'.
    Raises:
        ValueError: If the 'OPENAI_API_KEY' environment variable is not set.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")

client = openai.OpenAI()

def split_text_by_paragraphs(text, max_length=4096):
    """
    Splits a given text into chunks by paragraphs without exceeding a specified maximum length.
    
    Args:
        text (str): The text to be split.
        max_length (int): The maximum length allowed for each chunk. Default is 4096 characters.
    
    Returns:
        list: A list of text chunks, each not exceeding the maximum length.
    """
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk + '\n' + paragraph) <= max_length:
            current_chunk += ('\n' if current_chunk else '') + paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = paragraph
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def process_text_chunks(text_chunks):
    """
    Processes each text chunk, converting it to speech, saving the output as MP3 files.
    
    Args:
        text_chunks (list): A list of text chunks.
    """
    file_paths = []
    for i, chunk in enumerate(text_chunks):
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=chunk,
        )
        file_name = f"output_part_{i}.mp3"
        response.stream_to_file(file_name)
        file_paths.append(file_name)
        print(f"Part {i} complete. The audio has been saved to {file_name}.")
    return file_paths

def concatenate_mp3_files(file_paths, output_path="output_combined.mp3"):
    """
    Concatenates multiple MP3 files into a single MP3 file.
    
    Args:
        file_paths (list): Paths to the MP3 files to concatenate.
        output_path (str): The path for the output MP3 file.
    """
    combined = AudioSegment.empty()
    for file_path in file_paths:
        audio_segment = AudioSegment.from_mp3(file_path)
        combined += audio_segment
    combined.export(output_path, format="mp3")
    print(f"All parts have been combined into {output_path}.")

def main():
    """
    Main function to run the text-to-speech conversion and file concatenation.
    """
    set_openai_api_key()
    
    file_name = input("Enter the name of the text file: ")
    try:
        with open(file_name, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        print("File not found. Please check the file name and try again.")
        return

    text_chunks = split_text_by_paragraphs(file_content)
    generated_file_paths = process_text_chunks(text_chunks)
    concatenate_mp3_files(generated_file_paths)

if __name__ == "__main__":
    main()
