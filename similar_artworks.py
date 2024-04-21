import subprocess
import json
import requests

def get_xapp_token(client_id, client_secret):
    """Obtain an XAPP Token using the client ID and client secret using curl with verbose output."""
    url = f"https://api.artsy.net/api/tokens/xapp_token?client_id={client_id}&client_secret={client_secret}"
    curl_command = ["curl", "-v", "-X", "POST", url]
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        print("Curl verbose output:")
        print(result.stderr)  # Print the verbose output to understand the request and response headers
        token_info = json.loads(result.stdout)
        if 'token' in token_info:
            return token_info['token']
        else:
            print("Token not found in response")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to obtain XAPP Token: {e}")
        print(e.stderr)  # Display error output
        return None

def setup_session():
    """Set up a requests session with a browser-like User-Agent."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
    })
    return session

def search_artwork_by_name(session, access_token, artwork_name):
    """Search for an artwork by name and return the ID of the first artwork found."""
    url = "https://api.artsy.net/api/search"
    params = {'q': artwork_name, 'type': 'artwork'}
    headers = {"X-XAPP-Token": access_token}
    print(f"Searching for artwork: {artwork_name}...")
    response = session.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json().get('_embedded', {}).get('results', [])
        if not results:
            print(f"No artwork found matching the name: {artwork_name}")
            return None
        first_artwork = results[0]
        artwork_id = first_artwork['_links']['self']['href'].split('/')[-1]
        artwork_title_found = first_artwork['title']
        print(f"Found Artwork ID: {artwork_id} for '{artwork_title_found}'")
        return artwork_id
    else:
        print(f"Failed with status code: {response.status_code}, response: {response.text}")
        return None

def get_similar_artworks(session, access_token, artwork_id):
    """Fetch and display similar artworks based on artwork ID."""
    url = f'https://api.artsy.net/api/artworks?similar_to_artwork_id={artwork_id}'
    headers = {'X-XAPP-Token': access_token}
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        artworks_data = response.json()
        similar_artworks = artworks_data.get('_embedded', {}).get('artworks', [])
        if similar_artworks:
            print(f"\nSimilar Artworks for Artwork ID {artwork_id}:")
            for artwork in similar_artworks:
                title = artwork.get('title', 'No title provided')
                artist_name = artwork.get('_embedded', {}).get('artists', [{}])[0].get('name', 'Artist name not available')
                print(f"Title: {title}, Artist: {artist_name}")
        else:
            print("No similar artworks found.")
    else:
        print(f"Failed to fetch similar artworks. Status code: {response.status_code}")
        print("Response:", response.text)

if __name__ == '__main__':
    client_id = '3e0c75d3c7e77dadb74c'
    client_secret = '12fb7c20ea61647ac884d510884d0ffa'
    access_token = get_xapp_token(client_id, client_secret)
    
    if not access_token:
        print("Could not obtain an access token. Exiting.")
        exit(1)
    
    session = setup_session()
    artwork_name = input("Please enter the artwork name you are searching for: ")
    artwork_id = search_artwork_by_name(session, access_token, artwork_name)
    
    if artwork_id:
        get_similar_artworks(session, access_token, artwork_id)
    else:
        print("Failed to find the artwork.")
