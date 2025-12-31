from scripts.utils import get_spotify_client

sp = get_spotify_client()

# Lista ID artisti seed
ids = ['5QS9NAK4AgJPTcRe472pZA', '4q3ewBCX7sLwd24euuV69X', '5XJDexmWFLWOkjOEjOVX3e', '7iK8PXO48WeuP03g8YR51W', '1mcTU81TzQhprhouKaTkpq', '0eHQ9o50hj6ZDNBt6Ys1sD', '2LRoIwlKmHjgvigdNGBHNo', '0GM7qgcRCORpGnfcN2tCiB', '1i8SpTcr7yvPOmcqrbnVXY', '4SsVbpTthjScTS7U2hmr1X', '4obzFoKoKRHIphyHzJ35G3', '790FomKkXshlbRYZFtlgla', '3qsKSpcV3ncke3hw52JSMB', '2R21vXR83lH98kGeO99Y66', '12vb80Km0Ew53ABfJOepVz', '4VMYDCV2IEDYJArk749S6m', '77ziqFxp5gaInVrF2lj4ht', '0Q8NcsJwoCbZOHHW63su5S', '4aSlfXDn9R60UlbZEboBUy', '52iwsT98xCoGgiGntTiR7K', '5eumcnUkdmGvkvcsx1WFNG', '0elWFr7TW8piilVRYJUe4P', '0XeEobZplHxzM9QzFQWLiR', '6XkjpgcEsYab502Vr1bBeW', '12GqGscKJx3aE4t07u7eVZ', '0pePYDrJGk8gqMRbXrLJC8', '6Sbl0NT50roqWvy746MfVf', '7Gi6gjaWy3DxyilpF1a8Is', '3l9G1G9MxH6DaRhwLklaf5', '0ys2OFYzWYB5hRDLCsBqxt', '1dKdetem2xEmjgvyymzytS', '4UqfXEVibVEPfoopm7Pduc', '5bSfBBCxY8QAk4Pifveisz', '49EE6lVLgU8sp7dFgPshgM', '0v7JYEoQOQbzNNESKwxmzT', '2C6i0I5RiGzDKN9IAF8reh', '1KUm2LsC3HnPKHvIoo4cKu', '1bAftSH8umNcGZ0uyV7LMg', '716NhGYqD1jl2wI1Qkgq36', '2UZIAOlrnyZmyzt1nuXr9y', '0AqlFI0tz2DsEoJlKSIiT9', '0cr0zp1CI5bVOrXaVzfpUI', '4IRXvbsbSP4oHm4adUdQlt', '3QchzUOTSCKWmaRGEEiuir', '6w3SkAHYPsQ1bxV7VDlG5y', '3vQ0GE3mI0dAaxIMYe5g7z', '4m6ubhNsdwF4psNf3R8kwR', '19HM5j0ULGSmEoRcrSe5x3', '04mTej6RpWzBxGwhfThpIi', '1Yj5Xey7kTwvZla8sqdsdE']

print("Recupero dati da Spotify...")

# Recupero informazioni artisti
artist_list = []

for artist_id in ids:
    try:
        artist = sp.artist(artist_id)
        artist_list.append((artist['name'], artist['id']))
        print(f"Recuperato: {artist['name']}")
    except Exception as e:
        print(f"Errore con l'ID {artist_id}: {e}")

artist_list.sort(key=lambda x: x[0].lower())

# Salvataggio file seeds
with open('seeds.txt', 'w', encoding='utf-8') as f:
    for name, aid in artist_list:
        f.write(f"{name}, {aid}\n")

print(f"\nSuccesso! Creato seeds.txt con {len(artist_list)} artisti in ordine alfabetico.")