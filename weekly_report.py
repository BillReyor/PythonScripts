""" Experimental test code to summarize calendars given an ics export """
import sys
import os
import glob  # For pattern matching on file names
import datetime
from icalendar import Calendar

def check_dependency(module_name):
    """
    Attempts to import a module by name. Returns True if successful, False otherwise.
    """
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def ensure_dependencies():
    """
    Ensures all required dependencies are installed.
    """
    dependencies = ["icalendar", "torch", "transformers", "llama_cpp"]
    missing_dependencies = [dep for dep in dependencies if not check_dependency(dep)]

    if missing_dependencies:
        print("The following dependencies are missing:")
        for dep in missing_dependencies:
            print(f"- {dep}. To install, run: pip install {dep}")
        sys.exit("Exiting due to missing dependencies.")

def process_ics_file(file_path, start_date, end_date):
    """
    Processes the events from the specified ICS file and generates a detailed report for a specified date range,
    grouped by day.
    """
    with open(file_path, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    events_by_day = {}
    for component in cal.walk():
        if component.name == "VEVENT":
            dtstart = component.get('dtstart').dt
            summary = str(component.get('summary'))
            description = str(component.get('description')) if component.get('description') else "No description"
            location = str(component.get('location')) if component.get('location') else "No location specified"
            
            dtstart_str = dtstart.strftime("%Y-%m-%d %H:%M") if isinstance(dtstart, datetime.datetime) else dtstart.strftime("%Y-%m-%d")
            dtstart_date = dtstart.date() if isinstance(dtstart, datetime.datetime) else dtstart
            
            if start_date <= dtstart_date <= end_date:
                event_details = f"Event: {summary}\nTime: {dtstart_str}\nDescription: {description}\nLocation: {location}\n"
                if dtstart_date not in events_by_day:
                    events_by_day[dtstart_date] = [event_details]
                else:
                    events_by_day[dtstart_date].append(event_details)
    
    sorted_events_by_day = sorted(events_by_day.items())
    return sorted_events_by_day

def analyze_and_summarize(text, llm, user_name, event_date):
    """
    Analyzes and summarizes the given text using the Llama model, focusing on clarity, structure, and actionable insights.
    Each summary starts with "On [date], I..."
    """
    prompt = f"""<s>[INST] My name is {user_name}. This is my calendar please creating a summary of what I did during the day in paragraph form. Organize the day from early to late. .
    IGNORE / DO NOT INCLUDE personal habits like Decompression, self-care, etc.;
    IGNORE / DO NOT INCLUDE sensitive or confidential information including zoom links, passwords, or personal details.
    On {event_date.strftime('%d-%m-%Y')}, I Events: {text} [/INST]</s>"""

    output = llm(
        prompt,
        max_tokens=32768,
        stop=["</s>"],
        echo=False
    )
    
    if isinstance(output, dict) and 'choices' in output:
        response = output['choices'][0]['text'] if output['choices'] else "No response generated."
    else:
        response = str(output)

    with open('summary.txt', 'a') as file:
        file.write("On " + event_date.strftime('%d-%m-%Y') + ", I " + response + "\n\n")  
    
    return response

def finalize_summary(llm):
    """
    Reads the content from summary.txt, organizes it by day, and writes the final, grouped summary to final_summary.txt.
    """
    with open('summary.txt', 'r') as file:
        text = file.read()
    prompt = f"""<s>[INST] Create a narrative of what I did during the week. Be sure to create a summary for each day of the week starting with the earlies to latest the date is formated as (YYYY-MM-DD) .:
    : {text} [/INST]</s>"""
    
    output = llm(
        prompt,
        max_tokens=32768,
        stop=["</s>"],
        echo=False
    )
    
    if isinstance(output, dict) and 'choices' in output:
        final_response = output['choices'][0]['text'] if output['choices'] else "No final summary generated."
    else:
        final_response = str(output)

    with open('final_summary.txt', 'w') as file:
        file.write(final_response)

    print("Final summary has been organized by day and written to final_summary.txt.")

def main():
    ensure_dependencies()
    
    user_name = input("Please enter your name: ")
    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")

    start_date = datetime.datetime.strptime(start_date_input, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_input, "%Y-%m-%d").date()
    
    import torch
    from transformers import AutoTokenizer
    from llama_cpp import Llama

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model_path = "./mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    
    if not os.path.exists(model_path):
        sys.exit("Model file not found. Please download the model file before proceeding.")
    
    llm = Llama(model_path=model_path, n_ctx=32768, n_threads=8, n_gpu_layers=35)
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

    ics_files = glob.glob('*.ics')
    if not ics_files:
        sys.exit("No .ics files found in the current directory.")

    open('summary.txt', 'w').close()

    for file_path in ics_files:
        print(f"Processing {file_path}...")
        sorted_events_by_day = process_ics_file(file_path, start_date, end_date)

        for date, events in sorted_events_by_day:
            day_events_text = "\n".join(events)
            analyze_and_summarize(day_events_text, llm, user_name, date)

    finalize_summary(llm)
    
if __name__ == "__main__":
    main()
