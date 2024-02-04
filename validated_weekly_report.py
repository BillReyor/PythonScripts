"""
This script is designed for processing .ics (iCalendar) files to generate concise summaries of events within a user-defined date range. It leverages Llama CPP for text summarization and requires specific system and software prerequisites.

System Requirements:
- Compatible with M1 Mac (or later versions) equipped with a minimum of 16GB of RAM for optimal performance.

Software Dependencies:
- Python packages: Before running the script, ensure the installation of required Python packages: `re`, `datetime`, `glob`, `os`, `sys`, `icalendar`, `torch`, `transformers`, `llama-cpp-python`, `pytz`, and `tzlocal` using pip.

Model File Requirement:
- The Llama model file named 'mistral-7b-instruct-v0.2.Q4_K_M.gguf' must be present in the same directory as the script. It is essential for text summarization and can be downloaded from the specified source (source not provided).

Instructions for Use:
1. Place .ics calendar files in the same directory as this script.
2. Execute the script and enter your name along with the start and end dates for the event summary when prompted.
3. The script allows adjustments in `n_ctx` (up to 32768) and `max_tokens` parameters in `analyze_and_summarize` and `finalize_summary` functions to manage the summary output according to system memory capability. Note: A `n_ctx` of 32768 requires at least 16GB of RAM. The default setting is 16384.

This script is structured to first process the .ics files to filter events within the specified range, then analyze and summarize the event details using the Llama model, and finally consolidate the summaries into a comprehensive report.
"""


import re
import glob
import os
import sys
import pytz
import torch
import datetime
from tzlocal import get_localzone
from icalendar import Calendar
from transformers import AutoTokenizer
from llama_cpp import Llama

def sanitize_information(text):
    """Sanitize sensitive information from text."""
    patterns = [
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  
        r"\(\d{3}\)\s\d{3}-\d{4}",  
        r"\+\d{1,3}\s?(\(\d{1,3}\))?\s?\d{1,4}[\s-]?\d{1,4}[\s-]?\d{1,4}(?:[\s-]?\d{1,4})?",  
        r"\bhttps?:\/\/[^\s]+",  
        r"\bMeeting ID: \S+",  
        r"\bPasscode: \S+",  
        r"\bPIN: \d+",  
        r"\bID: \d{9,11}",  
    ]
    for pattern in patterns:
        text = re.sub(pattern, '[redacted]', text, flags=re.IGNORECASE)
    return text

def process_ics_file(file_path, start_date, end_date, user_tz):
    """Process ICS file events within a specified date range considering time zones."""
    with open(file_path, 'rb') as file:
        calendar = Calendar.from_ical(file.read())

    user_timezone = user_tz

    events_by_day = {}
    for component in calendar.walk():
        if component.name == "VEVENT":
            dtstart = component.get('dtstart').dt
            
            if isinstance(dtstart, datetime.datetime):
                if dtstart.tzinfo is None:
                    dtstart = dtstart.replace(tzinfo=user_timezone)
                else:
                    dtstart = dtstart.astimezone(user_timezone)
                dtstart_str = dtstart.strftime("%Y-%m-%d %H:%M")
                event_date = dtstart.date()
            else:
                dtstart_str = dtstart.strftime("%Y-%m-%d")
                event_date = dtstart

            summary = str(component.get('summary'))
            description = sanitize_information(str(component.get('description'))) if component.get('description') else "No description"
            if "This event was created by" in description:
                continue  # Skip the rest of the loop and do not include this event
            location = str(component.get('location')) if component.get('location') else "No location specified"
            location = sanitize_information(location)

            if start_date <= event_date <= end_date:
                event_details = (
                    f"Event: {summary}\n"
                    f"Time: {dtstart_str}\n"
                    f"Description: {description}\n"
                    f"Location: {location}\n"
                )
                events_by_day.setdefault(event_date, []).append(event_details)

    sorted_events_by_day = sorted(events_by_day.items(), key=lambda x: x[0])

    return sorted_events_by_day

def analyze_and_summarize(text, llm, user_name, event_date, summary_file='summary.txt'):
    """Analyze and summarize text using Llama model, outputting to specified file."""
    print(f"Analyzing and consolidate events for {event_date} in {summary_file}...")
    example = """
I. [Date]
    A. [Time]: [Event title]
        * [Event detail]
    B. [Time]: [Event title]
        * [Event detail]
    and so on...
    """
    
    prompt = f"""
<s>[INST] This is my calendar entry for 
{event_date.strftime('%m-%d-%Y')} (mm-dd-yyyy) Report what I did during 
the day. Keep it short and concise.  

Ensure that:
- Duplicate info is combined
- Output is sorted from early to late.
- If you are uncertain indicate that something is unknown rather than making it up
- Ignore the actual formatting and structure and follow the styling from the example:
{example}

Actual day: {text} [/INST]</s>
"""

    output = llm(prompt=prompt, max_tokens=2048, stop=["</s>"], echo=False)
    response = output['choices'][0]['text'] if output.get('choices') else "No response generated."

    with open(summary_file, 'a') as file:
        file.write(f"{response}\n\n")

    return response

def finalize_summary(llm):
    """Finalize summary by organizing content from two summaries."""
    # Modify this part to read both summaries and create a combined final summary
    with open('summary.txt', 'r') as file1:
        text1 = file1.read().strip()
    with open('summary2.txt', 'r') as file2:
        text2 = file2.read().strip()

    prompt = f"""<s>[INST] Fact check and summerize,  review the information from the first and second summary IGNORE any event not in both. Create a consolidated final weekly report by day.

First summary data:
{text1}

Second summary data:
{text2} [/INST]</s>"""

    output = llm(prompt=prompt, max_tokens=16384, stop=["</s>"], echo=False)
    final_response = output['choices'][0]['text'] if output.get('choices') else "No final summary generated."

    with open('final_summary.txt', 'w') as file:
        file.write(final_response)

    print("Final summary has been organized and written to 'final_summary.txt'.")

def main():
    user_name = input("Please enter your name: ")
    start_date_input = input("Enter the start date (mm-dd-yyyy): ")  
    end_date_input = input("Enter the end date (mm-dd-yyyy): ")
    user_tz = get_localzone()
    start_date = datetime.datetime.strptime(start_date_input, "%m-%d-%Y").date()
    end_date = datetime.datetime.strptime(end_date_input, "%m-%d-%Y").date()

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model_path = "./mistral-7b-instruct-v0.2.Q4_K_M.gguf"

    if not os.path.exists(model_path):
        sys.exit("Model file not found. Please download the model file before proceeding.")

    llm = Llama(model_path=model_path, n_ctx=8192, n_threads=16, n_gpu_layers=35)
    llm2 = Llama(model_path=model_path, n_ctx=16384, n_threads=16, n_gpu_layers=35)
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

    ics_files = glob.glob('*.ics')
    if not ics_files:
        sys.exit("No .ics files found in the current directory.")

    # Clear out old summaries
    open('summary.txt', 'w').close()
    open('summary2.txt', 'w').close()

    for file_path in ics_files:
        print(f"Processing {file_path}...")
        sorted_events_by_day = process_ics_file(file_path, start_date, end_date, user_tz)
        for date, events in sorted_events_by_day:
            day_events_text = "\n".join(events)
            analyze_and_summarize(day_events_text, llm, user_name, date, 'summary.txt')
            analyze_and_summarize(day_events_text, llm, user_name, date, 'summary2.txt')

    finalize_summary(llm2)

if __name__ == "__main__":
    main()
