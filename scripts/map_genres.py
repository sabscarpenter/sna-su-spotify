import pandas as pd
from collections import Counter

# Carica i dati
df = pd.read_csv('../data/gephi/nodes.csv')

# Raccogli tutti i generi unici
all_genres = []
for genres_str in df['genres'].dropna():
    genres = [g.strip() for g in genres_str.split(';') if g.strip()]
    all_genres.extend(genres)

# Conta i generi
genre_counts = Counter(all_genres)

print("=== GENERI PIÙ COMUNI ===")
print(f"Totale generi unici: {len(genre_counts)}\n")
for genre, count in genre_counts.most_common(50):
    print(f"{genre}: {count}")

# Definisci il mapping dei generi a categorie comuni
GENRE_MAPPING = {
    # Reggaeton e varianti
    'reggaeton': 'reggaeton',
    'reggaeton chileno': 'reggaeton',
    'reggaeton mexa': 'reggaeton',
    
    # Trap e varianti
    'trap': 'trap',
    'trap latino': 'trap',
    'argentine trap': 'trap',
    'chilean trap': 'trap',
    'mexican hip hop': 'trap',
    'latin hip hop': 'trap',
    
    # Corridos e varianti
    'corrido': 'corridos',
    'corridos tumbados': 'corridos',
    'corridos bélicos': 'corridos',
    'electro corridos': 'corridos',
    'sad sierreño': 'corridos',
    'sierreño': 'corridos',
    
    # Urbano Latino
    'urbano latino': 'urbano',
    'pop urbano': 'urbano',
    
    # Banda y música mexicana
    'banda': 'banda',
    'norteño': 'banda',
    'grupera': 'banda',
    'música mexicana': 'banda',
    'ranchera': 'banda',
    'mariachi': 'banda',
    'cumbia norteña': 'banda',
    'tejano': 'banda',
    
    # Latin general
    'latin': 'latin',
    'latin pop': 'latin',
    'latin alternative': 'latin',
    
    # Dembow
    'dembow': 'dembow',
    'dembow belico': 'dembow',
    
    # Mambo y variantes chilenas
    'mambo': 'mambo',
    'chilean mambo': 'mambo',
    
    # Hyperpop y experimental
    'hyperpop': 'hyperpop',
    'neoperreo': 'experimental',
    'experimental': 'experimental',
    
    # Hip hop y rap
    'hip hop': 'hip hop',
    'rap': 'hip hop',
    'old school hip hop': 'hip hop',
    'east coast hip hop': 'hip hop',
    'southern hip hop': 'hip hop',
    'melodic rap': 'hip hop',
    'boom bap': 'hip hop',
    
    # Afro
    'afrobeats': 'afro',
    'afrobeat': 'afro',
    'afropop': 'afro',
    'afropiano': 'afro',
    'afroswing': 'afro',
    'afro r&b': 'afro',
    'latin afrobeats': 'afro',
    
    # Cumbia
    'cumbia': 'cumbia',
    'cuarteto': 'cumbia',
    'electrocumbia': 'cumbia',
    
    # EDM y electrónica
    'edm': 'electronic',
    'dubstep': 'electronic',
    'electro': 'electronic',
    'electronic': 'electronic',
    'tech house': 'electronic',
    'hard techno': 'electronic',
    'big room': 'electronic',
    'moombahton': 'electronic',
    
    # RKT y Turreo
    'rkt': 'rkt',
    'turreo': 'rkt',
    
    # Bachata y otros ritmos caribeños
    'bachata': 'bachata',
    'salsa': 'salsa',
    'merengue': 'merengue',
    'vallenato': 'vallenato',
    
    # K-pop
    'k-pop': 'k-pop',
    'k-rap': 'k-pop',
    
    # Funk brasileiro
    'brazilian funk': 'funk brasileiro',
    'funk carioca': 'funk brasileiro',
    'funk pop': 'funk brasileiro',
    'brega funk': 'funk brasileiro',
    
    # Otros
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
    """Mappa i generi di un artista ai generi comuni"""
    if pd.isna(genres_str) or not genres_str:
        return ''
    
    genres = [g.strip() for g in genres_str.split(';') if g.strip()]
    
    # Mappa ogni genere
    mapped = []
    for genre in genres:
        if genre in GENRE_MAPPING:
            mapped_genre = GENRE_MAPPING[genre]
            if mapped_genre not in mapped:  # Evita duplicati
                mapped.append(mapped_genre)
        else:
            # Generi non mappati (lascia come "other" o ignora)
            if 'other' not in mapped and len(mapped) < 2:
                pass  # Ignora generi non mappati
    
    # Prendi al massimo 2 generi principali
    return ';'.join(mapped[:2]) if mapped else ''

# Applica il mapping
df['genres_mapped'] = df['genres'].apply(map_genres)

# Statistiche
print("\n\n=== STATISTICHE MAPPING ===")
print(f"Artisti totali: {len(df)}")
print(f"Artisti con generi originali: {df['genres'].notna().sum()}")
print(f"Artisti con generi mappati: {df['genres_mapped'].str.len().gt(0).sum()}")

# Conta i generi mappati
mapped_genres = []
for genres_str in df['genres_mapped']:
    if genres_str:
        genres = [g.strip() for g in genres_str.split(';') if g.strip()]
        mapped_genres.extend(genres)

mapped_counts = Counter(mapped_genres)
print("\n=== GENERI MAPPATI (TOP 20) ===")
for genre, count in mapped_counts.most_common(20):
    print(f"{genre}: {count}")

# Salva il risultato
output_path = '../data/gephi/nodes_mapped.csv'
df.to_csv(output_path, index=False)
print(f"\n✓ File salvato in: {output_path}")

# Mostra alcuni esempi
print("\n=== ESEMPI DI MAPPING ===")
sample = df[df['genres_mapped'].str.len() > 0].head(10)
for _, row in sample.iterrows():
    print(f"\n{row['name']}:")
    print(f"  Originale: {row['genres']}")
    print(f"  Mappato: {row['genres_mapped']}")
