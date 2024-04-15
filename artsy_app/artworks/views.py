from django.http import JsonResponse
import requests
import json

def get_token(request):
    # Parameters for obtaining user token
    cid = '6bb5b39fa796dfeccfdb'
    cs = '7a1bf2224a3b2aafb0cfcb0c141888fb'
    token_url = f'https://api.artsy.net/api/tokens/xapp_token?client_id={cid}&client_secret={cs}'

    # Make a POST request to get the user token
    response = requests.post(token_url)
    data = response.json()
    user_token = data.get('token', None)

    return JsonResponse({'token': user_token})

def get_artworks(request):
    # Get the user token by calling the get_token function
    token_response = get_token(request)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        return JsonResponse({'error': 'Failed to obtain user token'})
    # API endpoint to get artworks
    artworks_url = 'https://api.artsy.net/api/artworks?total_count=1'

    # Make a GET request with the user token in the header
    headers = {'X-XAPP-Token': user_token}
    response = requests.get(artworks_url, headers=headers)
    artworks_data = response.json()

    return JsonResponse(artworks_data)