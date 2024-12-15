from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Spotify API Credentials
CLIENT_ID = "03a27a036e72483bab2fab11686899a8"
CLIENT_SECRET = "6947f2eaf19847d6b83f4ab21ae16d9e"

# Initialize Spotify Client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Pretrained Data
try:
    music = pickle.load(open('df.pkl', 'rb'))  # DataFrame containing song data
    similarity = pickle.load(open('similarity.pkl', 'rb'))  # Similarity matrix
    print("Dataset and similarity matrix loaded successfully!")
    print("First few songs in dataset:", music['song'].head())  # Debugging
except FileNotFoundError:
    print("Make sure 'df.pkl' and 'similarity.pkl' are in the same directory as this script.")
    exit()

# Root Route
@app.route('/')
def home():
    return "Flask is running! Access /songs or /recommend to interact with the API."

# Fetch All Songs Endpoint
@app.route('/songs', methods=['GET'])
def get_all_songs():
    try:
        # Return all song names from the dataset
        songs = music['song'].tolist()
        print("Sending song list:", songs[:5])  # Debugging
        return jsonify({"songs": songs})
    except Exception as e:
        print("Error in /songs endpoint:", e)
        return jsonify({"error": "Unable to fetch song list."}), 500

# Fetch Album Cover from Spotify
def get_song_album_cover_url(song_name, artist_name):
    try:
        search_query = f"track:{song_name} artist:{artist_name}"
        results = sp.search(q=search_query, type="track", limit=1)
        if results and results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            return track["album"]["images"][0]["url"]  # Return album cover URL
        else:
            print(f"No album cover found for {song_name} by {artist_name}")
            return "https://i.postimg.cc/0QNxYz4V/social.png"  # Default image
    except Exception as e:
        print(f"Spotify API error for {song_name} by {artist_name}: {e}")
        return "https://i.postimg.cc/0QNxYz4V/social.png"  # Default image

# Recommendation Function
def recommend(song):
    try:
        # Find the index of the song
        index = music[music['song'] == song].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_music_names = []
        recommended_music_posters = []
        for i in distances[1:6]:
            artist = music.iloc[i[0]].artist
            song_name = music.iloc[i[0]].song
            recommended_music_names.append(song_name)
            recommended_music_posters.append(get_song_album_cover_url(song_name, artist))
        return recommended_music_names, recommended_music_posters
    except IndexError as e:
        print(f"Error in recommend function: {e}")
        return [], []

# Recommendation Endpoint
@app.route('/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        song_name = data.get('song', None)
        if not song_name:
            return jsonify({"error": "No song provided"}), 400

        recommended_music_names, recommended_music_posters = recommend(song_name)
        if not recommended_music_names:
            return jsonify({"error": "No recommendations found."}), 404

        return jsonify({
            "songs": recommended_music_names,
            "posters": recommended_music_posters
        })
    except Exception as e:
        print("Error in /recommend endpoint:", e)
        return jsonify({"error": "An internal error occurred"}), 500

# Run Flask App
if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)