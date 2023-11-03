import os
from dotenv import load_dotenv
import base64
import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup
from flask import render_template
from flask import Blueprint




app = Flask(__name__)
load_dotenv()

class SpotifyAPI:
    # ... (class definition and methods as provided in the previous response)
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()

    def get_token(self):
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(url, headers=headers, data=data)
        token_data = response.json()
        access_token = token_data.get("access_token")
        return access_token

    def search_tunisian_artists(self):
        url =  "https://api.spotify.com/v1/search?q=country%3ATunisia%2Cgenre%3Arap+tunisien%2Ctunisian+pop%2Ctunisian%2Carabic+hip+hop%2C&type=artist&market=TN&limit=50"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "q": "country:Tunisia,genre:rap tunisien,tunisian pop,tunisian,arabic hip hop,",
            "type": "artist",
            "limit": 50  # Number of artists to retrieve, adjust as needed
        }
        response = requests.get(url, headers=headers, params=params)
        artists_data = response.json()

        for artist in artists_data.get("artists", {}).get("items", []):
            artist_id = artist.get("id")
            streams = self.get_monthly_listeners(artist_id)  # Appel de la fonction get_monthly_listeners
            streams_number = int(streams.replace(",","").split()[0])

            artist["streams"] = streams_number  # Ajout de l'attribut "streams" à l'objet JSON de l'artiste

        return artists_data

    def tunisian_albums(self, artist_id, country='TN'):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "limit": 50  ,# Number of albums to retrieve, adjust as needed,
            "q" : "include_groups:single, album" 
        }
        response = requests.get(url, headers=headers, params=params)
        artists_albums_data = response.json()
        albums_info = []
        for album in artists_albums_data['items']:
            album_id = album['id']
            album_name = album['name']
            album_type = album['album_type']
            artists = [artist['name'] for artist in album['artists']]
            release_date = album.get('release_date')
            album_info = {
                "name": album_name,
                "type": album_type,
                #"artists": artists,
                #"release_date": release_date
            }
            albums_info.append(album_info)
        return albums_info 
    
    def get_monthly_listeners(self, artist_id, country='TN'):
        url = f"https://open.spotify.com/intl-fr/artist/{artist_id}"
        '''
        headers = {s
            "Authorization": f"Bearer {self.token}",

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        '''
        try:
            #response = requests.get(url, headers=headers)
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad requests (4xx and 5xx)
            '''
            if "sMT6JaxLhI2QLVSevX_3 fjP8GyQyM5IWQvTxWk6W" in response.text:
                print("\nfound\n")
            '''

            soup = BeautifulSoup(response.content, 'html.parser')
            div_element = soup.find('div', class_='Type__TypeElement-sc-goli3j-0 ieTwfQ sMT6JaxLhI2QLVSevX_3 fjP8GyQyM5IWQvTxWk6W')
            if div_element:
                # Affichage du texte contenu dans la div
                return(div_element.text)

        except requests.exceptions.RequestException as e:
            print(f"Request to Spotify API failed: {e}")
            


    def get_artist_albums(self, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "limit": 20,  # Number of albums to retrieve, adjust as needed
            "include_groups": "album",  # Filter for albums only
        }
        response = requests.get(url, headers=headers, params=params)
        albums_data = response.json()
        return albums_data

    def get_tracks(self, album_id):
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "limit": 20  # Number of tracks to retrieve, adjust as needed
        }
        response = requests.get(url, headers=headers, params=params)
        tracks_data = response.json()
        return tracks_data.get("items", [])
    


    def search_tunisian_albums(self):
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "q": "country:Tunisia,genre:rap tunisien,tunisian pop,tunisian,arabic hip hop",
            "type": "album",  # Search for albums instead of artists
            "limit": 50  # Number of albums to retrieve, adjust as needed
        }
        response = requests.get(url, headers=headers, params=params)
        albums_data = response.json()

        for album in albums_data.get("albums", {}).get("items", []):
            album_id = album.get("id")
            # Perform actions related to albums here if needed

        return albums_data  


spotify_api = SpotifyAPI('ab2ab72377844ee9810b7aeb46971c04', '3f46ba67ffd04e1d97d8341b19069d99')
@app.route('/')
def index():

    # Get Tunisian artists and their albums
    tunisian_artists_data = spotify_api.search_tunisian_artists()

    if "artists" in tunisian_artists_data:
        tunisian_artists = tunisian_artists_data["artists"]["items"]
        #tunisian_artists.sort(key=lambda x: int(x.get("streams", 0)), reverse=True)
        print(tunisian_artists)
        sorted_artists = sorted(tunisian_artists, key=lambda x: x["streams"], reverse=True)

        top_5_artists = sorted_artists[:5]
        formatted_artists = []

        for artist in top_5_artists:
     
            # Join album names into a single string separated by commas
            #album_names = ", ".join(album["name"] for album in artist_albums)
            
            artist_info = {
                "name": artist['name'],
                "followers": artist['followers']['total'],
                "popularity": artist['popularity'],
                "spotify_id": artist["id"],
                "streams": artist['streams'],
                #"albums": album_names  # Include albums as a single string in the response
            }


            formatted_artists.append(artist_info)


        # Return the formatted JSON response
        return jsonify(formatted_artists)
        #return render_template('index.html', artists=formatted_artists)

    else:
        return "No Tunisian artists found."
    '''
        # Get Tunisian artists and their albums
    tunisian_albums_data = spotify_api.search_tunisian_albums()

    if "albums" in tunisian_albums_data:
        tunisian_albums = tunisian_albums_data["albums"]["items"]
        #tunisian_artists.sort(key=lambda x: int(x.get("streams", 0)), reverse=True)
        print(tunisian_albums)
        sorted_albums = sorted(tunisian_albums, key=lambda x: x["release_date"], reverse=True)

        top_5_albums = sorted_albums[:20]
        formatted_albums = []

        for album in top_5_albums:
            
            # Join album names into a single string separated by commas
            #album_names = ", ".join(album["name"] for album in artist_albums)
            
            albums_info = {
                "name": album['name'],
                "album_type": album['album_type'],
                "artist" : album["artists"],
                "type": album['type'],
                "spotify_id": album["id"],
                "release_date ": album["release_date"],
                
                #"streams": album['streams'],
                #"albums": album_names  # Include albums as a single string in the response
            }
            formatted_albums.append(albums_info)
            

        # Return the formatted JSON response
        return jsonify(formatted_albums)
        #return render_template('index.html', artists=formatted_artists)

    else:
        return "No Tunisian artists found."
    '''


if __name__ == "__main__":
    app.run(debug=True ), #host='0.0.0.0', port=5000)
