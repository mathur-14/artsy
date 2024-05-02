from django.http import JsonResponse
from django.core.paginator import Paginator
from .helper import setup_session
import subprocess
from artsy_app.settings import db
import json
import time

artwork_projection = {
    '_id': 0,
    'id': 1,
    'slug': 1,
    'title': 1,
    'category': 1,
    'additional_information': 1,
    'medium': 1,
    'date': 1,
    'dimensions': 1,
    'artists': 1,
    '_links.thumbnail.href': 1,
    '_links.self.href': 1,
    '_links.similar_artworks.href': 1,
}

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
    
def get_paginated_artworks(request):
    collection = db['artworks']

    # Get the page number from the request query parameters
    page_number = int(request.GET.get('page', 1))
    page_size = 10

    # Get the total count of artworks
    total_artworks = collection.count_documents({})

    # Retrieve artworks from MongoDB with pagination
    artworks = list(collection.find({}, artwork_projection).skip((page_number - 1) * page_size).limit(page_size))

    # Create a Paginator instance
    paginator = Paginator(artworks, page_size)

    # Get the current page of artworks
    page_obj = paginator.get_page(page_number)

    # Prepare the response data
    response_data = {
        'count': total_artworks,
        'next': (page_number * page_size) < total_artworks,
        'previous': page_number > 1,
        'results': list(page_obj.object_list)
    }

    return JsonResponse(response_data)

def get_artwork_by_id(request, id):
    collection = db['artworks']

    # Retrieve artworks from MongoDB with pagination
    artwork = collection.find_one({'id': id}, artwork_projection)

    # Prepare the response data
    if(artwork):
        return JsonResponse(artwork)
    else:
        return JsonResponse({'message': f'Could not find any artwork with id: ${id}'})

def get_artwork_by_category(request, category):
    collection = db['artworks']

    # Get the page number from the request query parameters
    page_number = int(request.GET.get('page', 1))
    page_size = 10

    # Get the total count of artworks
    total_artworks = collection.count_documents({'category': category})

    # Retrieve artworks from MongoDB with pagination
    artworks = list(collection.find({'category': category}, artwork_projection).skip((page_number - 1) * page_size).limit(page_size))

    # Create a Paginator instance
    paginator = Paginator(artworks, page_size)

    # Get the current page of artworks
    page_obj = paginator.get_page(page_number)

    # Prepare the response data
    response_data = {
        'count': total_artworks,
        'next': (page_number * page_size) < total_artworks,
        'previous': page_number > 1,
        'results': list(page_obj.object_list)
    }

    return JsonResponse(response_data)

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
                        'gender': artist.get('gender', None),
                        'birthday': artist.get('birthday', None),
                        'deathday': artist.get('deathday', None),
                        'nationality': artist.get('nationality', None),
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

def get_artists(request):
    collection = db['artworks']

    # Query to get a list of unique artists with names and IDs
    pipeline = [
        {"$unwind": "$artists"},
        {"$group": {"_id": {"name": "$artists.name", "id": "$artists.id"}, "count": {"$sum": 1}}},
        {"$project": {"artist_name": "$_id.name", "artist_id": "$_id.id", "_id": 0}}
    ]

    result = collection.aggregate(pipeline)

    # Store unique artists in a list
    unique_artists = []
    for artist in result:
        unique_artists.append({"name": artist["artist_name"], "id": artist["artist_id"]})

    return JsonResponse(unique_artists, safe=False)

def get_categories(request):
    collection = db['artworks']
    result = collection.distinct('category')

    return JsonResponse(result, safe=False)

def get_artworks_by_artist(request, artist_id):
    collection = db['artworks']

    page_number = int(request.GET.get('page', 1))
    page_size = 10

    total_artworks = collection.count_documents({"artists.id": artist_id})

    artworks = list(collection.find({"artists.id": artist_id}, artwork_projection).skip((page_number - 1) * page_size).limit(page_size))

    paginator = Paginator(artworks, page_size)
    page_obj = paginator.get_page(page_number)

    response_data = {
        'count': total_artworks,
        'next': (page_number * page_size) < total_artworks,
        'previous': page_number > 1,
        'results': list(page_obj.object_list)
    }

    return JsonResponse(response_data)
