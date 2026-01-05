# Funzioni per raccogliere dati da Spotify API

import pandas as pd
import time


def get_artist_info(sp, artist_id):
    """Recupera le informazioni base di un artista dato il suo ID Spotify."""
    artist = sp.artist(artist_id)
    return {
        'id': artist['id'],
        'name': artist['name'],
        'popularity': artist['popularity'],
        'genres': artist['genres']
    }


def get_collaborations(sp, artist_id):
    """Trova tutte le collaborazioni di un artista analizzando i suoi album e singoli."""
    collaborations = []
    results = sp.artist_albums(artist_id, album_type='album,single', limit=50)
    albums = results['items']
    seen_tracks = set()

    for album in albums:
        time.sleep(0.2)
        tracks = sp.album_tracks(album['id'])['items']
        for track in tracks:
            if track['id'] not in seen_tracks:
                artists_in_track = [a['id'] for a in track['artists']]
                if len(artists_in_track) > 1:
                    for i in range(len(artists_in_track)):
                        for j in range(i + 1, len(artists_in_track)):
                            collaborations.append((artists_in_track[i], artists_in_track[j]))
                seen_tracks.add(track['id'])

    return list(set(collaborations))