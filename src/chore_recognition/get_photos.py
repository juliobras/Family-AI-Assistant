import os
import requests
import time

# Constants
ACCESS_KEY = 'hPeh4b_JRIgLrUDrp_xGhb8Exvz7vi_STwdRpWaOaxQ'
API_ENDPOINT = 'https://api.unsplash.com'
MAX_PHOTOS_PER_ROOM = 5000
PHOTOS_PER_BATCH = 500
REQUEST_LIMIT_PER_HOUR = 50
SLEEP_TIME = 3600  # One hour

# Define the room types and corresponding folder names
room_types = {
    'living_room': 'Living Room',
    'bedroom': 'Bedroom',
    'kitchen': 'Kitchen',
    'bathroom': 'Bathroom',
    'dining_room': 'Dining Room',
}

# Create a folder structure to save the images
base_folder = '/Users/julio/Documents/Home AI Assistant/Family-AI-Assistant/data/images/rooms/clean'
room_folders = {}

# Count initial files in each room's folder
file_counts = {}

for room_type in room_types:
    folder_name = room_types[room_type].lower().replace(' ', '_')
    room_folder = os.path.join(base_folder, folder_name)
    os.makedirs(room_folder, exist_ok=True)
    room_folders[room_type] = room_folder
    file_counts[room_type] = len(os.listdir(room_folder))  # Count existing files

# Function to handle API requests
def make_request(url, params):
    try:
        response = requests.get(url, params=params, headers={'Authorization': f'Client-ID {ACCESS_KEY}'})
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error: {e}")
        user_input = input("Do you wish to continue? (yes/no): ").strip().lower()
        return None if user_input != 'yes' else make_request(url, params)

request_count = 0

# Downloading images
while any(count < MAX_PHOTOS_PER_ROOM for count in file_counts.values()):
    for room_type, room_name in room_types.items():
        if file_counts[room_type] >= MAX_PHOTOS_PER_ROOM:
            continue  # Skip if already downloaded enough images for this room type

        room_folder = room_folders[room_type]

        # Fetch collection photos
        page = 1
        batch_count = 0
        while batch_count < PHOTOS_PER_BATCH and file_counts[room_type] < MAX_PHOTOS_PER_ROOM:
            get_photos_url = f"{API_ENDPOINT}/search/photos"
            params = {'query': room_name, 'page': page, 'per_page': 30}
            
            response = make_request(get_photos_url, params)
            if not response:
                continue  # Skip to next iteration if there was an error

            request_count += 1
            if request_count >= REQUEST_LIMIT_PER_HOUR:
                print("Reached API request limit, sleeping for one hour...")
                time.sleep(SLEEP_TIME)
                request_count = 0  # Reset request count after sleeping
            
            photos = response.json().get('results', [])
            if not photos:
                break  # No more photos available

            for photo in photos:
                photo_url = photo['urls']['regular']
                filename = os.path.join(room_folder, f'{photo["id"]}.jpg')

                try:
                    img_response = requests.get(photo_url)
                    img_response.raise_for_status()
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    print(f'Downloaded {photo["id"]}.jpg to {room_name} folder')
                    file_counts[room_type] += 1
                    batch_count += 1

                    if batch_count >= PHOTOS_PER_BATCH or file_counts[room_type] >= MAX_PHOTOS_PER_ROOM:
                        break  # Move to the next room type

                except requests.RequestException as e:
                    print(f"Failed to download {photo_url}: {e}")

            page += 1
