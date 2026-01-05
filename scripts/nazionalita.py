# Script per recuperare le nazionalità degli artisti da Wikidata

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import time

# Caricamento dati artisti
df_original = pd.read_csv('../data/new/grezzi/nodes.csv')
artist_data = df_original[['id', 'name']].drop_duplicates().values.tolist()


def get_artist_data_from_wikidata(spotify_id, artist_name):
    """Cerca la nazionalità di un artista su Wikidata tramite Spotify ID o nome."""
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url, agent="MusicResearchProject/1.0")
    sparql.setReturnFormat(JSON)
    
    # Query per cercare tramite Spotify ID
    query = f"""
    SELECT ?artistLabel ?countryLabel WHERE {{
      ?artist wdt:P1902 "{spotify_id}" .
      OPTIONAL {{
        {{ ?artist wdt:P19/wdt:P17 ?country . }}
        UNION
        {{ ?artist wdt:P495 ?country . }}
        UNION
        {{ ?artist wdt:P27 ?country . }}
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,es,en". }}
    }}
    LIMIT 1
    """
    
    try:
        sparql.setQuery(query)
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            data = results["results"]["bindings"][0]
            name = data.get("artistLabel", {}).get("value", "Unknown")
            country = data.get("countryLabel", {}).get("value", "Unknown")
            return name, country
        
        # Fallback: cerca per nome artista
        name_query = f"""
        SELECT ?artistLabel ?countryLabel WHERE {{
          ?artist rdfs:label "{artist_name}"@en .
          ?artist wdt:P31 wd:Q5 .
          {{ ?artist wdt:P106/wdt:P279* wd:Q639669 . }}
          UNION
          {{ ?artist wdt:P106 wd:Q177220 . }}
          OPTIONAL {{
            {{ ?artist wdt:P19/wdt:P17 ?country . }}
            UNION
            {{ ?artist wdt:P495 ?country . }}
            UNION
            {{ ?artist wdt:P27 ?country . }}
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,es,en". }}
        }}
        LIMIT 1
        """
        
        time.sleep(0.3)
        sparql.setQuery(name_query)
        name_results = sparql.query().convert()
        
        if name_results["results"]["bindings"]:
            data = name_results["results"]["bindings"][0]
            name = data.get("artistLabel", {}).get("value", artist_name)
            country = data.get("countryLabel", {}).get("value", "Unknown")
            return name, country
        
        return artist_name, "Unknown"
        
    except Exception as e:
        print(f"Errore per {artist_name}: {e}")
        return artist_name, "Error"


# Elaborazione artisti
risultati = []
total = len(artist_data)
unknown_count = 0
error_count = 0

print(f"Inizio recupero dati per {total} artisti")

for i, (s_id, s_name) in enumerate(artist_data):
    name, country = get_artist_data_from_wikidata(s_id, s_name)
    risultati.append({
        'spotify_id': s_id, 
        'name': name, 
        'country': country
    })
    
    if country == "Unknown":
        unknown_count += 1
    if country == "Error":
        error_count += 1
    
    if (i + 1) % 50 == 0:
        print(f"Processati {i+1}/{total}")

    time.sleep(0.5)

# Salvataggio risultati
df_nationalities = pd.DataFrame(risultati)
df_nationalities.to_csv('../data/new/nazioni/artisti-e-nazionalita.csv', index=False)

print(f"Completato. Totale: {total}, trovati: {total - unknown_count - error_count}, non trovati: {unknown_count}, errori: {error_count}")