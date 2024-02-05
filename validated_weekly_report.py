"""
This script is designed to generate event summaries from .ics calendar files within a specified date range. It extracts event details, sanitizes sensitive information, and uses a language model to produce consolidated summaries of daily activities.

Requirements:
- System: macOS with M1 chip (or later) and a minimum of 16GB RAM for efficient processing.
- Python Packages: Before running the script, ensure the following packages are installed: `re`, `datetime`, `glob`, `os`, `sys`, `icalendar`, `torch`, `transformers`, `llama-cpp-python`, `pytz`, and `tzlocal`. These can be installed via pip.
- Model File: The script requires the 'mistral-7b-instruct-v0.2.Q4_K_M.gguf' model file to be present in the script's directory. This file should be obtained from a verified source.

Usage Instructions:
1. Place any .ics calendar files to be processed in the same directory as this script.
2. Execute the script and enter your name along with the start and end dates for the event summary when prompted.
3. The script allows for adjusting the context size (`n_ctx`) up to 32768 and `max_tokens` for the language model in the `analyze_and_summarize` and `finalize_summary` functions to handle different sizes of summary generation. Note that larger context sizes require at least 16GB of RAM.

Key Functionalities:
- The script sanitizes personal information from event descriptions and locations to maintain privacy.
- It processes events within the user-specified date range, grouping them by day.
- Utilizes a language model to analyze and summarize daily events, producing a clear and concise summary for each day.
- The `finalize_summary` function compares summaries to ensure accuracy and resolves discrepancies, generating a final consolidated summary.

This script is suitable for individuals looking to obtain a summarized overview of their calendar events over a given period without manually combing through each entry.
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
    """
    Sanitizes personal information from a given text by replacing sensitive details
    with '[redacted]'. Patterns include emails, phone numbers, URLs, and meeting details.

    Args:
    - text: A string containing potentially sensitive information.

    Returns:
    - The sanitized string with sensitive information redacted.
    """
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
    """
    Processes an .ics calendar file, extracting and organizing event details
    within the specified date range. Events are sanitized for privacy.

    Args:
    - file_path: Path to the .ics file.
    - start_date, end_date: The date range to filter events.
    - user_tz: The timezone of the user for date-time conversions.

    Returns:
    - A list of tuples (date, events) sorted by date, where each event is a detailed string.
    """
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
                continue
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
                raw_event_file = f"raw_events_{event_date}.txt"
                with open(raw_event_file, 'a') as raw_file:
                    raw_file.write(event_details + "\n\n")
    sorted_events_by_day = sorted(events_by_day.items(), key=lambda x: x[0])
    return sorted_events_by_day

def analyze_and_summarize(text, llm, user_name, event_date, summary_file='summary.txt'):
    """
    Analyzes and summarizes a given text (representing events of a specific day) using a language model.

    Args:
    - text: The text containing event details to summarize.
    - llm: The language model object for generating summaries.
    - user_name: Name of the user for personalizing the summary.
    - event_date: The date of the events being summarized.
    - summary_file: The file path to write the summary to.

    Returns:
    - The generated summary of the events.
    """
    print(f"Analyzing and consolidating events for {event_date} in {summary_file}...")
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
    """
    Compares and consolidates summaries generated in previous steps to produce a final summary.
    May generate a third summary for further validation if discrepancies are detected.

    Args:
    - llm: The language model object used for generating and consolidating summaries.

    Returns:
    - None. The final summary is written to a file.
    """
    text1, text2, text3 = "", "", ""
    if os.path.exists('summary.txt'):
        with open('summary.txt', 'r') as file1:
            text1 = file1.read().strip()
    if os.path.exists('summary2.txt'):
        with open('summary2.txt', 'r') as file2:
            text2 = file2.read().strip()
    if os.path.exists('summary3.txt'):
        with open('summary3.txt', 'r') as file3:
            text3 = file3.read().strip()

    # Modification to ensure that the presence of text in summary3.txt is checked
    summaries_exist = text3 != ""

    # Adjusted the logic to handle cases when summary3.txt is empty or not needed
    if summaries_exist:
        # Modified to include correct logic when all summaries exist
        print("Comparing all three summaries to identify the most accurate consolidation...")
        prompt = """<s>[INST] Compare three summaries and identify the most accurate consolidation. 
First summary:
{text1}

Second summary:
{text2}

Third summary:
{text3}[/INST]</s>""".format(text1=text1, text2=text2, text3=text3)
    else:
        print("Evaluating the first two summaries for discrepancies...")
        prompt = """<s>[INST] Evaluate two summaries for discrepancies. Return 'MISMATCH' and STOP if any discrepancies exist. Otherwise, consolidate into a final report.
First summary:
{text1}

Second summary:
{text2}[/INST]</s>""".format(text1=text1, text2=text2)

    # Assuming the `llm` function call structure, needs adjustment based on actual LLM API
    output = llm(prompt=prompt, max_tokens=4096, stop=["</s>"], echo=False)
    final_response = output['choices'][0]['text'].strip() if output.get('choices') else "No response generated."

    if "MISMATCH" in final_response and not summaries_exist:
        # Modification to ensure a third summary is generated only when needed
        print("Discrepancy detected. Generating a third summary for further validation...")
        # Fixed the recursive call to avoid potential infinite loops
        current_date = datetime.datetime.now()
        analyze_and_summarize(text1 + "\n" + text2, llm, "Validation Run", current_date, 'summary3.txt')
        # Recursive call removed to prevent potential infinite loop
        # Call `finalize_summary` again only if necessary after reviewing the new `summary3.txt`
    elif "MISMATCH" in final_response and summaries_exist:
        print("Discrepancies detected even after three summaries. Attempting a final consolidation...")
        # Logic for further action if needed, potentially manual review
    else:
        if summaries_exist or not summaries_exist and "MISMATCH" not in final_response:
            print("Final consolidation derived from the available summaries.")
            with open('final_summary.txt', 'w') as file:
                file.write(final_response)
            print("Final summary has been organized and written to 'final_summary.txt'.")
def main():
    """
    Main function to execute the script. It processes .ics calendar files,
    generates summaries of events for a specified date range, and produces
    a final consolidated summary.

    Requires user input for name and date range.
    """
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
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

    ics_files = glob.glob('*.ics')
    if not ics_files:
        sys.exit("No .ics files found in the current directory.")

    open('summary.txt', 'w').close()
    open('summary2.txt', 'w').close()
    open('summary3.txt', 'w').close()  # Ensure this is also reset for a new run

    for file_path in ics_files:
        print(f"Processing {file_path}...")
        sorted_events_by_day = process_ics_file(file_path, start_date, end_date, user_tz)
        for date, events in sorted_events_by_day:
            day_events_text = "\n".join(events)
            analyze_and_summarize(day_events_text, llm, user_name, date, 'summary.txt')
            analyze_and_summarize(day_events_text, llm, user_name, date, 'summary2.txt')

    finalize_summary(llm)

if __name__ == "__main__":
    main()
