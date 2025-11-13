import os

import requests

BOT_URL = os.getenv("BOT_URL")
BOT_KEY=os.getenv("BOT_KEY")

def send_text_message(instance, number, text):
    url = f"{BOT_URL}/message/sendText/{instance.name}"
    payload = {
        "number": number,
        "options": {"delay": 8000, "presence": "composing"},
        "textMessage": {"text": text}
    }
    headers = {
        "apikey": BOT_KEY,
        "Content-Type": "application/json"
    }
    return requests.post(url, json=payload, headers=headers, timeout=60)


def send_media_message(instance, number, media_type, file_name, caption, media):
    url = f"{BOT_URL}/message/sendMedia/{instance.name}"
    payload = {
        "number": number,
        "options": {"delay": 8000, "presence": "composing"},
        "mediaMessage": {
            "mediatype": media_type,
            "fileName": file_name,
            "caption": caption,
            "media": media
        }
    }
    headers = {
        "apikey": BOT_KEY,
        "Content-Type": "application/json"
    }
    return requests.post(url, json=payload, headers=headers, timeout=60)



def send_audio_message(instance, number, audio):
    url = f"{BOT_URL}/message/sendWhatsAppAudio/{instance.name}"
    payload = {
        "number": number,
        "options": {"delay": 8000, "presence": "recording"},
        "audioMessage": {"audio": audio}
    }
    headers = {
        "apikey": BOT_KEY,
        "Content-Type": "application/json"
    }
    return requests.post(url, json=payload, headers=headers, timeout=60)