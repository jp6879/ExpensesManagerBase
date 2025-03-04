import json
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import unicodedata


def write_to_google_sheet(
    month,
    row=["25/08/2021", "JP", "ALQUILER", "SI", "NARANJA", "1", "1000", ""],
):
    """Function to write a row to a Google Sheet.
    Args:
        month (str): The month to write the row to.
        row (list): A list containing the row data.
    """
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # Path to the service account key file
    SERVICE_ACCOUNT_FILE = "app/credentials/service_account.json"

    # Authenticate using the service account
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    #FIXME: This should be in the config file 
    SPREADSHEET_ID = "INSERT_YOUR_SPREADSHEET_ID_HERE"
    RANGE = f"{month}!A:J"
    try:
        sheet = build("sheets", "v4", credentials=creds)
        values = [row]
        body = {"values": values}
        sheet.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")


def remove_accents(input_str):
    # Normalize the string to decompose accents
    normalized_str = unicodedata.normalize("NFD", input_str)
    # Remove the accents by filtering out combining marks
    return "".join(char for char in normalized_str if not unicodedata.combining(char))


def process_message(date, message):
    """Function to process a message and return a row to append to the Google Sheet.
    Args:
        date (str): The date of the message.
        message (str): The message to process.
    Returns:
        row (list): A list containing the processed row data.
    """
    CATEGORIES = [
        "ALQUILER",
        "DECO",
        "DELIVERY",
        "ELECTRONICOS",
        "HIGIENE",
        "MUEBLES",
        "ROPA",
        "SALIDA",
        "SERVICIOS",
        "SUPER",
        "TRANSPORTE",
        "VIAJES",
        "EDUCACIÓN",
        "REGALOS",
        "SALUD",
    ]

    # Splitting the message by .
    parts = remove_accents(message).upper().split(".")

    if len(parts) < 6:
        return "Invalid message format"

    month = parts[0]
    name = parts[1]
    category = parts[2].strip() if parts[2].strip() in CATEGORIES else "OTRO"
    in_cash = parts[3].strip() if parts[3].strip() in ["SI", "NO"] else "SI"
    credit_card = parts[4]

    cuotas = parts[5].strip() if parts[5].strip() else 1
    total = parts[6].strip() if parts[6].strip() else 0

    try:
        reintegros = parts[7].strip() if parts[7].strip() else 0
    except IndexError:
        reintegros = 0

    try:
        notes = parts[8].strip() if parts[8].strip() else ""
    except IndexError:
        notes = ""

    cuotas = int(cuotas)
    if cuotas > 1:
        total = float(total.replace(",", "."))
        cuotas_str = f"1/{cuotas}"
        total = str(round(float(total) / cuotas, 2)).replace(".", ",")
    else:
        cuotas_str = "1"

    row = [
        date,
        name,
        category,
        in_cash,
        credit_card,
        cuotas_str,
        total,
        notes,
        "",
        reintegros,
    ]

    return month, row


def store_and_process_message(sender, timestamp, text):
    """Function to create a log of messages received into a JSON file.
    args:
        sender (str): The sender of the message.
        timestamp (str): The timestamp of the message.
        text (str): The text of the message.
    returns:
        month (str): The sheet name.
        processed_row (str): The processed text.
    """
    # Define the log file
    file_name = "messages.json"

    # Read existing messages
    try:
        with open(file_name, "r") as file:
            messages = json.load(file)
    except FileNotFoundError:
        messages = []

    SENDER_DICT = {"number": "name"}

    # Convert the timestamp to a human-readable format
    date_format = datetime.fromtimestamp(int(timestamp)).strftime("%d/%m/%Y")
    sender_name = SENDER_DICT.get(sender, sender)

    # Process the message and get the month and row
    month, processed_row = process_message(date_format, text)  # Use OpenAI

    messages.append(
        {
            "sender": sender_name,
            "timestamp": date_format,
            "text": text,
            "month": month,
            "processed_text": processed_row,
        }
    )

    # TODO: This might excalate too much, maybe its a good idea to store this in a database
    # Write back to the file
    with open(file_name, "w") as file:
        json.dump(messages, file, indent=4)

    return month, processed_row
