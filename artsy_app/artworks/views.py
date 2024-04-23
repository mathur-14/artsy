from django.http import JsonResponse
from .helper import setup_session
import subprocess
import requests
import json

def get_token(request):
    # Parameters for obtaining user token
    cid = '6bb5b39fa796dfeccfdb'
    cs = '7a1bf2224a3b2aafb0cfcb0c141888fb'
    token_url = f'https://api.artsy.net/api/tokens/xapp_token?client_id={cid}&client_secret={cs}'

    curl_command = ["curl", "-v", "-X", "POST", token_url]
    
    try:
        # Make a POST request to get the user token
        response = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        data = json.loads(response.stdout)
        user_token = data.get('token', None)
        if user_token:
            return JsonResponse({'token': user_token})
        else:
            print("Token not found in response")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to obtain XAPP Token: {e}")
        print(e.stderr)  # Display error output
        return None

def get_artworks(request):
    # Get the user token by calling the get_token function
    token_response = get_token(request)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        return JsonResponse({'error': 'Failed to obtain user token'})
    
    session = setup_session()
    session.headers.update({'X-XAPP-Token': user_token})

    # API endpoint to get artworks
    artworks_url = 'https://api.artsy.net/api/artworks?total_count=1'

    # Make a GET request with the user token in the header
    response = session.get(artworks_url)
    if response.status_code == 200:
        artworks_data = response.json()
        return JsonResponse(artworks_data)
    else:
        return JsonResponse({'error': f'Failed to fetch artworks. Status code: {response.status_code}'})