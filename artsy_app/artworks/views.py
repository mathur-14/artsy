from django.http import JsonResponse
from .helper import setup_session
import subprocess
from artsy_app.settings import db
import json
import time

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

def get_artist_details(session, artwork):
    artists_url = artwork.get('_links', {}).get('artists', {}).get('href', None)
    if artists_url:
        retry_count = 0
        max_retries = 3
        retry_delay = 1  # Initial delay in seconds

        while retry_count < max_retries:
            artists_response = session.get(artists_url)
            if artists_response.status_code == 200:
                artists_data = artists_response.json().get('_embedded', {}).get('artists', [])
                artwork['artists'] = [
                    {
                        'id': artist.get('id'),
                        'name': artist.get('name'),
                        'gender': artist.get('gender'),
                        'birthday': artist.get('birthday'),
                        'deathday': artist.get('deathday'),
                        'nationality': artist.get('nationality'),
                        'artworks': artist.get('_links', {}).get('artworks', {}).get('href', None),
                        'similar_artists': artist.get('_links', {}).get('similar_artists', {}).get('href', None)
                    }
                    for artist in artists_data
                ]
                break
            else:
                retry_count += 1
                retry_delay *= 2  # Double the delay for the next retry
                print(f"Request failed with status code {artists_response.status_code}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        if retry_count == max_retries:
            print(f"Maximum retries ({max_retries}) exceeded for artists URL: {artists_url}")

def get_artists(request):
    # Get the user token by calling the get_token function
    token_response = get_token(request)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        return JsonResponse({'error': 'Failed to obtain user token'})
    
    session = setup_session()
    session.headers.update({'X-XAPP-Token': user_token})

    # API endpoint to get artists
    artists_url = 'https://api.artsy.net/api/artists'

    # Make a GET request with the user token in the header
    response = session.get(artists_url)
    if response.status_code == 200:
        artists_data = response.json()
        return JsonResponse(artists_data)
    else:
        return JsonResponse({'error': f'Failed to fetch artists. Status code: {response.status_code}'})

def put_artworks(request):
    # Get the user token by calling the get_token function
    token_response = get_token(request)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        return JsonResponse({'error': 'Failed to obtain user token'})
    
    session = setup_session()
    session.headers.update({'X-XAPP-Token': user_token})
    
    # API endpoint to get artworks
    artworks_url = 'https://api.artsy.net/api/artworks'
    artworks_data = []

    # Loop through paginated results
    while artworks_url:
        retry_count = 0
        max_retries = 3
        retry_delay = 1  # Initial delay in seconds

        while retry_count < max_retries:
            response = session.get(artworks_url)
            if response.status_code == 200:
                break
            else:
                retry_count += 1
                retry_delay *= 2  # Double the delay for the next retry
                print(f"Request failed with status code {response.status_code}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        if retry_count == max_retries:
            print(f"Maximum retries ({max_retries}) exceeded. Skipping to the next page.")
            next_page = None
        else:
            data = response.json()

            # Extract artworks from the current page
            artworks = data.get('_embedded', {}).get('artworks', [])
            for artwork in artworks:
                get_artist_details(session, artwork)
            
            artworks_data.extend(artworks)

            # Get the next page URL
            next_page = data.get('_links', {}).get('next', {}).get('href', None)

        artworks_url = next_page

    # Store artworks in MongoDB
    collection = db['artworks']
    try:
        result = collection.insert_many(artworks_data)
        return JsonResponse({'message': f'{len(result.inserted_ids)} artworks added to MongoDB'})
    except Exception as e:
        return JsonResponse({'message': 'Failed to insert records to the mongodb', 'error': str(e)}, status = 500)

# def put_artists(request):
#     # Get the user token by calling the get_token function
#     token_response = get_token(request)
#     token_data = json.loads(token_response.content)
#     user_token = token_data.get('token', None)

#     if user_token is None:
#         return JsonResponse({'error': 'Failed to obtain user token'})
    
#     session = setup_session()
#     session.headers.update({'X-XAPP-Token': user_token})
    
#     # API endpoint to get artists
#     artists_url = 'https://api.artsy.net/api/artists'
#     artists_data = []
#     print('here you are')
#     count=0
#     # Loop through paginated results
#     while artists_url:
#         retry_count = 0
#         max_retries = 3
#         retry_delay = 1  # Initial delay in seconds
#         print(count,':',artists_url)
#         count+=1
#         while retry_count < max_retries:
#             response = session.get(artists_url)
#             if response.status_code == 200:
#                 break
#             else:
#                 retry_count += 1
#                 retry_delay *= 2  # Double the delay for the next retry
#                 print(f"Request failed with status code {response.status_code}. Retrying in {retry_delay} seconds...")
#                 time.sleep(retry_delay)

#         if retry_count == max_retries:
#             print(f"Maximum retries ({max_retries}) exceeded. Skipping to the next page.")
#             next_page = None
#         else:
#             data = response.json()

#             # Extract artists from the current page
#             artists = data.get('_embedded', {}).get('artists', [])
#             artists_data.extend(artists)

#             # Get the next page URL
#             next_page = data.get('_links', {}).get('next', {}).get('href', None)

#         artists_url = next_page
#     print('here I am')
#     # Store artists in MongoDB
#     collection = db['artists']
#     try:
#         result = collection.insert_many(artists_data)
#         return JsonResponse({'message': f'{len(result.inserted_ids)} artists added to MongoDB'})
#     except Exception as e:
#         return JsonResponse({'message': 'Failed to insert records to the mongodb', 'error': str(e)}, status = 500)
