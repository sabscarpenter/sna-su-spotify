# Configurazione client Spotify con autenticazione

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()


def get_spotify_client():
    """Crea e restituisce un client Spotify autenticato usando le credenziali dal file .env"""
    auth_manager = SpotifyClientCredentials(
        client_id=os.getenv('SPOTIPY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
    )
    return spotipy.Spotify(auth_manager=auth_manager, requests_timeout=10, retries=10)