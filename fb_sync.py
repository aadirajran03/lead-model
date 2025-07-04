import requests

def get_facebook_leads(access_token, page_id, form_id):
    url = f"https://graph.facebook.com/v19.0/{form_id}/leads"
    params = {
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print("Facebook API Error:", response.text)
        return []
