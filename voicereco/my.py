import whisper
import spacy
import datetime
import json
import os
import re 
import dateparser
from datetime import datetime

# Initialize Whisper model
model = whisper.load_model("base")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# File to store appointments
APPOINTMENTS_FILE = "appointments.json"

def recognize_speech():
    print("Listening... Speak now.")
    # For simplicity, we'll use a recorded audio file. In a real app, you'd capture live audio.
    result = model.transcribe("Recording.m4a")
    return result["text"]

def process_command(text):
    print(f"Original text: {text}")

    # Extract time using regex
    time_pattern = r'\b(?:1[0-2]|0?[1-9])(?::?[0-5][0-9])?\s*(?:a\.?m\.?|p\.?m\.?)\b'
    time_match = re.search(time_pattern, text, re.IGNORECASE)
    time = time_match.group() if time_match else None
    print(f"Extracted time: {time}")

    # Parse the date
    date_pattern = r'\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})\b'
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    date_str = date_match.group() if date_match else None
    print(f"Extracted date string: {date_str}")

    if date_str:
        parsed_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})
        date = parsed_date.strftime("%Y-%m-%d") if parsed_date else None
    else:
        date = None
    print(f"Formatted date: {date}")

    # Extract purpose (assuming it's the remaining text)
    purpose = re.sub(time_pattern, '', text, flags=re.IGNORECASE)
    purpose = re.sub(date_pattern, '', purpose, flags=re.IGNORECASE)
    purpose = purpose.strip()

    return {"date": date, "time": time, "purpose": purpose}

# Test the function
sample_input = "Can you make a booking with Dr. Tant for on 2nd of January 2025 at 11 a.m. please?"
result = process_command(sample_input)
print("Result:", result)

# Test the function
sample_inputs = [
    "Book a doctor's appointment for tomorrow at 10am",
    "Schedule a meeting on January 2nd, 2025 at 2:30pm",
    "Book an appointment for tomorrow 2nd of January 2020-5 at 11am"
]

for input_text in sample_inputs:
    print("\nTesting input:", input_text)
    result = process_command(input_text)
    print("Result:", result)
    print("-" * 50)

def check_availability(date, time):
    appointments = load_appointments()
    for appointment in appointments:
        if appointment["date"] == date and appointment["time"] == time:
            return False
    return True

def book_appointment(details):
    appointments = load_appointments()
    appointments.append(details)
    save_appointments(appointments)

def load_appointments():
    if os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_appointments(appointments):
    with open(APPOINTMENTS_FILE, "w") as f:
        json.dump(appointments, f)

def main():
    while True:
        print("\nReady to book an appointment. Speak your request.")
        voice_input = recognize_speech()
        print(f"You said: {voice_input}")
        
        appointment_details = process_command(voice_input)
        print(f"Processed details: {appointment_details}")
        
        if not appointment_details["date"] or not appointment_details["time"]:
            print("Sorry, I couldn't understand the date or time. Please try again.")
            continue
        
        if check_availability(appointment_details["date"], appointment_details["time"]):
            book_appointment(appointment_details)
            print("Appointment booked successfully!")
        else:
            print("Time slot not available. Please choose another.")
        
        choice = input("Do you want to book another appointment? (yes/no): ")
        if choice.lower() != "yes":
            break

if __name__ == "__main__":
    main()
