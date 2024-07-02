import requests
from bs4 import BeautifulSoup
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

scope = "playlist-modify-public playlist-modify-private user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path="token.txt"))

username = sp.current_user()["display_name"]
user_id = sp.current_user()["id"]
results = sp.current_user_saved_tracks()


# for i, item in enumerate(results['items']):
#     track = item['track']
#     print(i, track['artists'][0]['name'], " – ", track['name'])

def get_song_uri(song_name, year):
    query = f"track:{song_name} year:{year}"
    res = sp.search(q=query, type="track", limit=1)
    if res['tracks']['items']:
        track = res['tracks']['items'][0]
        return track['uri']
    else:
        return None


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
date_obj = datetime.strptime(date, "%Y-%m-%d")
formatted_date = date_obj.strftime("%B %d, %Y")
year = date[:4]

# getting the billboard 100 from the date inputted
response = requests.get("https://www.billboard.com/charts/hot-100/" + date)
print("https://www.billboard.com/charts/hot-100/" + date)
# turning the html into song names using beautiful soup
soup = BeautifulSoup(response.text, "html.parser")
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]

# keeping track of all uri's for the corresponding song
all_uri = []
for song in song_names:
    if get_song_uri(song, year):
        all_uri.append(get_song_uri(song, year))

# create a new playlist with the data we collected from the
# billboard top 100 on the corresponding date
playlist_name = f"{formatted_date} Billboard Top 100"
playlist_description = (f"A playlist created with the use of Spotipy | Data from the Billboard Top 100 "
                        f"on the date: {formatted_date} that was chosen when this program was run")
new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)
playlist_id = new_playlist["id"]
print(f"Created Playlist: {new_playlist}, ID: {playlist_id}")

sp.playlist_add_items(playlist_id, all_uri)
