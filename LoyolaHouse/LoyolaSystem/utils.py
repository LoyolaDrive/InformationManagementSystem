import requests

def set_viber_webhook():
    viber_api_url = "https://chatapi.viber.com/pa/set_webhook"
    headers = {
        "X-Viber-Auth-Token": "547ee03c13b8e3c2-b0bd072aff139c17-1b4114e20b76e52a",
        "Content-Type": "application/json"
    }

    payload = {
        "url": "https://f243-103-62-153-140.ngrok-free.app/viber_webhook/",
        "event_types": ["subscribed", "unsubscribed", "message", "delivered"],
        "send_name": True,
        "send_photo": True
    }

    response = requests.post(viber_api_url, json=payload, headers=headers)
    
    print("Webhook Setup Response:", response.json())
    return response.status_code, response.json()


import requests

def get_bot_info():
    viber_api_url = "https://chatapi.viber.com/pa/get_account_info"
    headers = {
        "X-Viber-Auth-Token": "547ee03c13b8e3c2-b0bd072aff139c17-1b4114e20b76e52a",
        "Content-Type": "application/json"
    }

    response = requests.post(viber_api_url, headers=headers)
    print("Bot Info:", response.json())
    return response.status_code, response.json()