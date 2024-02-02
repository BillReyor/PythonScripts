"""
This script is tailored for processing ICS calendar files to extract, summarize, and compile a comprehensive overview of events scheduled for a given week. Initially, it verifies the availability of essential dependencies, including 'icalendar', 'torch', 'transformers', and 'llama_cpp'. The script processes the ICS file to delineate events within the current week, organizing them by day. Utilizing the Llama model (Mistral 7B Instruct version), it generates concise summaries for each day's events. These daily summaries are then aggregated and further condensed into a final summary, encapsulating the week's key activities and highlights in a succinct narrative.

Functions:
- check_dependencies(): Checks for the installation of required dependencies, ensuring the script's prerequisites are met.
- process_ics_file(file_path): Parses the ICS file to extract and group events by day for the current week, preparing them for summarization.
- analyze_and_summarize(text, llm): Summarizes the provided text using the Llama model, creating concise summaries of daily events.
- finalize_summary(llm): Compiles the daily summaries from 'summary.txt', producing a final, overarching summary of the week's events, which is saved to 'final_summary.txt'.
- main(): Coordinates the script's operations, from dependency verification and event extraction to the generation of daily and final weekly summaries.
"""

import sys
import datetime
from icalendar import Calendar
import os
import torch
from transformers import AutoTokenizer
from llama_cpp import Llama

def check_dependencies():
    """
    Ensures that all required dependencies are installed. Checks for the presence of the icalendar, torch, 
    transformers, and llama_cpp packages. If any are missing, the script exits with an error message prompting 
    the user to install the missing package.
    """
    try:
        from icalendar import Calendar
    except ImportError:
        sys.exit("Dependency missing: icalendar. To install, run: pip install icalendar")
    
    try:
        import torch
    except ImportError:
        sys.exit("Dependency missing: torch. To install, run: pip install torch")
    
    try:
        from transformers import AutoTokenizer
    except ImportError:
        sys.exit("Dependency missing: transformers. To install, run: pip install transformers")
    
    try:
        from llama_cpp import Llama
    except ImportError:
        sys.exit("Dependency missing: llama_cpp. Please ensure it is correctly installed.")

def process_ics_file(file_path):
    """
    Reads and processes an ICS file to extract calendar events for the current week. It groups events by day,
    collecting event details such as summary, description, start time, and location.

    Args:
        file_path (str): The path to the ICS file.

    Returns:
        A sorted list of tuples, each containing a date and a list of event details for that date.
    """
    with open(file_path, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    
    events_by_day = {}
    for component in cal.walk():
        if component.name == "VEVENT":
            dtstart = component.get('dtstart').dt
            summary = str(component.get('summary'))
            description = str(component.get('description')) if component.get('description') else "No description"
            location = str(component.get('location')) if component.get('location') else "No location specified"
            
            dtstart_str = dtstart.strftime("%Y-%m-%d %H:%M") if isinstance(dtstart, datetime.datetime) else dtstart.strftime("%Y-%m-%d")
            dtstart_date = dtstart.date() if isinstance(dtstart, datetime.datetime) else dtstart
            
            if start_of_week <= dtstart_date <= end_of_week:
                event_details = f"Event: {summary}\nTime: {dtstart_str}\nDescription: {description}\nLocation: {location}\n"
                if dtstart_date not in events_by_day:
                    events_by_day[dtstart_date] = [event_details]
                else:
                    events_by_day[dtstart_date].append(event_details)
    
    sorted_events_by_day = sorted(events_by_day.items())
    return sorted_events_by_day

def analyze_and_summarize(text, llm):
    """
    Uses the Llama model to generate a summary of the provided text. The function constructs a prompt for the model
    and processes the text to create a concise summary.

    Args:
        text (str): The text to summarize.
        llm (Llama): An instance of the Llama model.

    Returns:
        A string containing the summarized text.
    """
    prompt = f"<s>[INST] You are tasked with creating concise summaries from calendar events. For each event, summarize it into a paragraph as a topic covered. Include an overview, key points, day it happened, and any actionable insights related to that event. Events: {text} [/INST]</s>"
    
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

    with open('summary.txt', 'a') as file:  # Append mode to accumulate daily summaries
        file.write(response)
    
    return response

def finalize_summary(llm):
    """
    Reads the accumulated summaries from summary.txt, summarizes them to create a final summary of the week,
    and writes this final summary to final_summary.txt. This process provides a high-level overview of the week's events.

    Args:
        llm (Llama): An instance of the Llama model.
    """
    with open('summary.txt', 'r') as file:
        text = file.read()

    prompt = f"<s>[INST] You are tasked with creating a concise summary of the weekly events based on the detailed summaries provided. Summarize the key activities, important meetings, and notable personal time offs into a cohesive summary that highlights the main focus and achievements of the week. Detailed summaries: {text} [/INST]</s>"

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

    with open('final_summary.txt', 'w') as file:
        file.write(response)

    print("Final summary has been written to final_summary.txt")

def main():
    """
    Main function to orchestrate the script's operations. It checks for necessary dependencies, initializes the
    Llama model, processes an ICS file to extract events, summarizes these events, and finally generates a
    comprehensive summary of the week's events.
    """
    check_dependencies()
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model_path = "./mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        sys.exit("Model file not found. Please download the model file before proceeding.")
    
    llm = Llama(model_path=model_path, n_ctx=32768, n_threads=8, n_gpu_layers=35)
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

    file_path = input("Please enter the path to your ICS file: ")
    if not os.path.exists(file_path):
        sys.exit(f"File not found: {file_path}")

    sorted_events_by_day = process_ics_file(file_path)

    # Clear summary.txt before processing
    open('summary.txt', 'w').close()

    for date, events in sorted_events_by_day:
        print(f"\nProcessing date: {date}")
        day_events_text = "\n".join(events)
        print(f"Summarizing events for {date}:")
        print(day_events_text)
        analyze_and_summarize(day_events_text, llm)

    # Summarize the entire week's events into a final summary
    finalize_summary(llm)
    
if __name__ == "__main__":
    main()
