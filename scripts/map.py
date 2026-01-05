# Script per mappare i generi musicali in categorie semplificate

import pandas as pd
from collections import Counter

# Caricamento dati
df = pd.read_csv('../data/new/grezzi/nodes.csv')

# Estrazione generi
all_genres = []
for genres_str in df['genres'].dropna():
    genres = [g.strip() for g in genres_str.split(';') if g.strip()]
    all_genres.extend(genres)

genre_counts = Counter(all_genres)

# Dizionario di mapping generi
GENRE_MAPPING = {
    'reggaeton': 'reggaeton',
    'reggaeton chileno': 'reggaeton',
    'reggaeton mexa': 'reggaeton',
    
    'trap': 'trap',
    'argentine trap': 'trap',
    'trap latino': 'trap',
    'chilean trap': 'trap',
    'mexican hip hop': 'trap',
    'latin hip hop': 'trap',
    'urbano latino': 'trap',
    'pop urbano': 'trap',
    
    'corrido': 'corridos',
    'corridos tumbados': 'corridos',
    'corridos bélicos': 'corridos',
    'electro corridos': 'corridos',
    'sad sierreño': 'corridos',
    'sierreño': 'corridos',
    
    'banda': 'banda',
    'norteño': 'banda',
    'grupera': 'banda',
    'música mexicana': 'banda',
    'ranchera': 'banda',
    'mariachi': 'banda',
    'cumbia norteña': 'banda',
    'tejano': 'banda',
    
    'latin': 'latin',
    'latin pop': 'latin',
    'latin alternative': 'latin',
    
    'dembow': 'dembow',
    'dembow belico': 'dembow',
    
    'mambo': 'mambo',
    'chilean mambo': 'mambo',
    
    'hyperpop': 'hyperpop',

    'neoperreo': 'experimental',
    'experimental': 'experimental',
    
    'hip hop': 'hip hop',
    'rap': 'hip hop',
    'old school hip hop': 'hip hop',
    'east coast hip hop': 'hip hop',
    'southern hip hop': 'hip hop',
    'melodic rap': 'hip hop',
    'boom bap': 'hip hop',
    
    'afrobeats': 'afro',
    'afrobeat': 'afro',
    'afropop': 'afro',
    'afropiano': 'afro',
    'afroswing': 'afro',
    'afro r&b': 'afro',
    'latin afrobeats': 'afro',
    
    'cumbia': 'cumbia',
    'cuarteto': 'cumbia',
    'electrocumbia': 'cumbia',
    
    'edm': 'electronic',
    'dubstep': 'electronic',
    'electro': 'electronic',
    'electronic': 'electronic',
    'tech house': 'electronic',
    'hard techno': 'electronic',
    'big room': 'electronic',
    'moombahton': 'electronic',
    
    'rkt': 'rkt',
    'turreo': 'rkt',
    
    'bachata': 'bachata',
    'salsa': 'salsa',
    'merengue': 'merengue',
    'vallenato': 'vallenato',
    
    'k-pop': 'k-pop',
    'k-rap': 'k-pop',
    
    'brazilian funk': 'funk brasileiro',
    'funk carioca': 'funk brasileiro',
    'funk pop': 'funk brasileiro',
    'brega funk': 'funk brasileiro',
    
    'pop': 'pop',
    'soft pop': 'pop',
    'colombian pop': 'pop',
    'brazilian pop': 'pop',
    'dancehall': 'dancehall',
    'drill': 'drill',
    'uk drill': 'drill',
    'phonk': 'phonk',
    'drift phonk': 'phonk',
    'techengue': 'techengue',
}


def map_genres(genres_str):
    """Mappa i generi originali nelle categorie semplificate."""
    if pd.isna(genres_str) or not genres_str:
        return ''
    
    genres = [g.strip() for g in genres_str.split(';') if g.strip()]
    
    mapped = []
    for genre in genres:
        if genre in GENRE_MAPPING:
            mapped_genre = GENRE_MAPPING[genre]
            if mapped_genre not in mapped:
                mapped.append(mapped_genre)
        else:
            if 'other' not in mapped and len(mapped) < 2:
                pass
    
    return ';'.join(mapped[:2]) if mapped else ''


# Applicazione mapping e salvataggio
df['genres_mapped'] = df['genres'].apply(map_genres)

output_path = '../data/new/generi-mappati.csv'
df.to_csv(output_path, index=False)

# Statistiche
print(f"Artisti totali: {len(df)}")
print(f"Artisti con generi originali: {df['genres'].notna().sum()}")
print(f"Artisti con generi mappati: {df['genres_mapped'].str.len().gt(0).sum()}")
print(f"File salvato in: {output_path}")
