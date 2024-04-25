import time
import json
from datetime import datetime
from artsy_app.settings import db
from django.utils import timezone
from artworks.views import setup_session, get_token

import logging
logger = logging. getLogger(__name__)

def run_cron_job():
    print('here')
    logger.debug('cron job has started') 
    fetch_artworks()

def fetch_artworks():
    # Get the user token
    token_response = get_token(None)
    token_data = json.loads(token_response.content)
    user_token = token_data.get('token', None)

    if user_token is None:
        logger.debug('Failed to obtain user token')
        return

    session = setup_session()
    session.headers.update({'X-XAPP-Token': user_token})

    # API endpoint to get artworks
    artworks_url = 'https://api.artsy.net/api/artworks'
    artworks_data = []

    # Loop through paginated results
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
                logger.debug(f"Request failed with status code {response.status_code}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        if retry_count == max_retries:
            logger.debug(f"Maximum retries ({max_retries}) exceeded. Skipping to the next page.")
            next_page = None
        else:
            data = response.json()

            # Extract artworks from the current page
            artworks = data.get('_embedded', {}).get('artworks', [])
            artworks_data.extend(artworks)

            # Get the next page URL
            next_page = data.get('_links', {}).get('next', {}).get('href', None)

        artworks_url = next_page

    # Process the fetched artworks
    process_artworks(artworks_data)

def process_artworks(artworks_data):
    for artwork_data in artworks_data:
        artwork_id = artwork_data['id']
        created_at = artwork_data['created_at']
        updated_at = artwork_data['updated_at']

        # Convert datetime strings to Django's timezone-aware datetime objects
        created_at = timezone.make_aware(datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S%z'))
        updated_at = timezone.make_aware(datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%S%z'))

        # Check if the artwork exists in the database
        collection = db['artworks']
        artwork = collection.find_one({"id": artwork_id})

        if artwork:
            # Artwork exists, check if it needs to be updated
            if artwork.updated_at < updated_at:
                # Update the artwork
                collection.update_one({"id": artwork_id}, {"$set": artwork_data})
                logger.debug(f'Updated artwork with ID {artwork_id}')
        else:
            # Artwork doesn't exist, create a new one
            collection.insert_one(artwork_data)
            logger.debug(f'Added new artwork with ID {artwork_id}')
