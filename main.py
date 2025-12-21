import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

def test_collaborations(artist_name="Marracash"):
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # 1. Trova l'artista
    results = sp.search(q='artist:' + artist_name, type='artist')
    artist_id = results['artists']['items'][0]['id']
    print(f"✅ Artista trovato: {artist_name}")

    # 2. Ottieni gli album/singoli
    albums = sp.artist_albums(artist_id, album_type='album,single', limit=10)
    
    collaborators = set()
    
    print(f"Analizzando le collaborazioni negli ultimi dischi...")
    for album in albums['items']:
        # 3. Ottieni le tracce di ogni album
        tracks = sp.album_tracks(album['id'])
        for track in tracks['items']:
            # Se ci sono più artisti nella traccia, c'è un arco (collaborazione)!
            if len(track['artists']) > 1:
                names = [a['name'] for a in track['artists']]
                for name in names:
                    if name != artist_name:
                        collaborators.add(name)
    
    print(f"✅ Trovati {len(collaborators)} collaboratori unici:")
    print(list(collaborators)[:10]) # Mostra i primi 10

if __name__ == "__main__":
    test_collaborations()