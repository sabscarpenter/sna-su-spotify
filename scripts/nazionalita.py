import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import time

df_original = pd.read_csv('../data/pesata/nodes.csv')
# Creo una lista di tuple (id, name)
artist_data = df_original[['id', 'name']].drop_duplicates().values.tolist()

def get_artist_data_from_wikidata(spotify_id, artist_name):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url, agent="MusicResearchProject/1.0")
    sparql.setReturnFormat(JSON)
    
    # Prima query: cerca con ID Spotify - priorità a luogo di nascita e origine
    query = f"""
    SELECT ?artistLabel ?countryLabel WHERE {{
      ?artist wdt:P1902 "{spotify_id}" .
      OPTIONAL {{
        {{ ?artist wdt:P19/wdt:P17 ?country . }}  # Luogo di nascita → paese
        UNION
        {{ ?artist wdt:P495 ?country . }}  # Paese di origine
        UNION
        {{ ?artist wdt:P27 ?country . }}  # Cittadinanza (ultimo fallback)
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
        
        # Fallback: cerca per nome se l'ID Spotify non ha dato risultati
        print(f"  ID non trovato per {artist_name}, provo con il nome...")
        name_query = f"""
        SELECT ?artistLabel ?countryLabel WHERE {{
          ?artist rdfs:label "{artist_name}"@en .
          ?artist wdt:P31 wd:Q5 .
          {{ ?artist wdt:P106/wdt:P279* wd:Q639669 . }}
          UNION
          {{ ?artist wdt:P106 wd:Q177220 . }}
          OPTIONAL {{
            {{ ?artist wdt:P19/wdt:P17 ?country . }}  # Luogo di nascita → paese
            UNION
            {{ ?artist wdt:P495 ?country . }}  # Paese di origine
            UNION
            {{ ?artist wdt:P27 ?country . }}  # Cittadinanza (ultimo fallback)
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,es,en". }}
        }}
        LIMIT 1
        """
        
        time.sleep(0.3)  # Piccolo delay per non sovraccaricare
        sparql.setQuery(name_query)
        name_results = sparql.query().convert()
        
        if name_results["results"]["bindings"]:
            data = name_results["results"]["bindings"][0]
            name = data.get("artistLabel", {}).get("value", artist_name)
            country = data.get("countryLabel", {}).get("value", "Unknown")
            
            return name, country
        
        return artist_name, "Unknown"  # Almeno restituisco il nome dal CSV
        
    except Exception as e:
        print(f"Errore per {artist_name} ({spotify_id}): {e}")
        return artist_name, "Error"

risultati = []
total = len(artist_data)
unknown_country_count = 0
error_count = 0
fallback_count = 0

print(f"Inizio recupero dati per {total} artisti...")

for i, (s_id, s_name) in enumerate(artist_data):
    name, country = get_artist_data_from_wikidata(s_id, s_name)
    risultati.append({
        'spotify_id': s_id, 
        'name': name, 
        'country': country
    })
    
    if country == "Unknown":
        unknown_country_count += 1
    if country == "Error":
        error_count += 1
    if name != s_name and name != "Unknown" and name != "Error":
        fallback_count += 1
    
    if (i + 1) % 10 == 0:
        print(f"Processati {i+1}/{total}... (Paese sconosciuto: {unknown_country_count}, Errors: {error_count}, Fallback: {fallback_count})")

    time.sleep(0.5)  # Aumentato da 0.4 a 0.5 per evitare rate limiting

df_nationalities = pd.DataFrame(risultati)
df_nationalities.to_csv('../data/artisti-e-nazionalita.csv', index=False)

print("\nFatto! File 'artisti-e-nazionalita.csv' creato con successo.")
print(f"Totale artisti: {total}")
print(f"Paesi trovati: {total - unknown_country_count - error_count}")
print(f"Paesi non trovati: {unknown_country_count}")
print(f"Ricerche con fallback (nome): {fallback_count}")
print(f"Errori: {error_count}")
print("\nPrime righe del risultato:")
print(df_nationalities.head())