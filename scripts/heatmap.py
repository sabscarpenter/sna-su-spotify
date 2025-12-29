import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Palette estratta da Gephi
gephi_palette = [
    "#845D95", "#FB71FF", "#F6B2FB", "#A947C7", 
    "#BF84F9", "#C1A2F8", "#F659F7", "#7F69C6", 
    "#9C5B9E", "#DC7AF2", "#F4C0F7", "#8E7AF2"
]

# Crea una colormap con sfumatura dal bianco a viola
gephi_cmap = LinearSegmentedColormap.from_list("gephi", ["#FFFFFF", "#F4C0F7", "#BF84F9", "#A947C7", "#845D95"])

# Carica i dati con i generi mappati
# Prima esegui map_genres.py per creare nodes_mapped.csv
try:
    df = pd.read_csv('../data/gephi/nodes_mapped.csv')
    genre_column = 'genres_mapped'
    print("✓ Usando generi mappati")
except FileNotFoundError:
    df = pd.read_csv('../data/gephi/nodes.csv')
    genre_column = 'genres'
    print("⚠ File mappato non trovato, usando generi originali")
    print("  Esegui prima: python map_genres.py")

# Rimuovi le righe con generi mancanti
df_clean = df[df[genre_column].notna()].copy()
df_clean = df_clean[df_clean[genre_column].str.len() > 0].copy()

# Espandi i generi (ogni artista può avere più generi separati da ";")
genres_expanded = []
for idx, row in df_clean.iterrows():
    genres = row[genre_column].split(';')
    community = row['modularity_class']
    for genre in genres:
        genre = genre.strip()
        if genre:  # Ignora stringhe vuote
            genres_expanded.append({
                'community': community,
                'genre': genre
            })

# Crea DataFrame con i generi espansi
df_genres = pd.DataFrame(genres_expanded)

# Crea matrice di conteggio: comunità x genere
heatmap_data = pd.crosstab(df_genres['community'], df_genres['genre'])

# Assicurati che tutte le comunità siano presenti (anche quelle senza generi mappati)
all_communities = sorted(df['modularity_class'].unique())
heatmap_data = heatmap_data.reindex(all_communities, fill_value=0)

# Ordina le comunità
heatmap_data = heatmap_data.sort_index()

# Conta i generi
genre_counts = df_genres['genre'].value_counts()

# Se ci sono più di 15 generi, prendi i top 15, altrimenti tutti
num_genres = min(15, len(genre_counts))
top_genres = genre_counts.head(num_genres).index
heatmap_data_filtered = heatmap_data[top_genres]

# Ordina le colonne alfabeticamente
heatmap_data_filtered = heatmap_data_filtered[sorted(heatmap_data_filtered.columns)]

# Converti in percentuali sul totale della comunità
# Calcola il numero totale di artisti per comunità (considerando che ogni artista può avere più generi)
community_totals = df_clean.groupby('modularity_class').size()
heatmap_data_percentage = heatmap_data_filtered.div(community_totals, axis=0) * 100

fig_width = max(12, len(top_genres) * 0.8)
fig_height = max(8, len(heatmap_data_filtered) * 0.5)
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

sns.heatmap(heatmap_data_percentage, 
            annot=True, 
            fmt='.1f', 
            cmap=gephi_cmap,
            cbar_kws={'label': 'Percentuale (%)'},
            linewidths=0.5,
            square=False,
            ax=ax)

plt.title('Distribuzione dei Generi Musicali per Comunità\n(Analisi Omofilia di Genere)', 
          fontsize=16, pad=20)
plt.xlabel('Genere Musicale', fontsize=12)
plt.ylabel('Comunità (modularity_class)', fontsize=12)
plt.xticks(rotation=90, ha='center')
plt.tight_layout()

# Salva la figura
plt.savefig('../report/heatmap_genre_homophily.png', dpi=300, bbox_inches='tight')
print("Heatmap salvata in: ../report/heatmap_genre_homophily.png")

# Mostra la heatmap
plt.show()

# Stampa statistiche aggiuntive
print("\n=== STATISTICHE OMOFILIA DI GENERE ===\n")
print(f"Numero totale di comunità: {df_clean['modularity_class'].nunique()}")
print(f"Numero totale di generi unici: {len(genre_counts)}")
print(f"\nTop 10 generi più comuni:")
print(genre_counts.head(10))

# Calcola l'indice di concentrazione per ogni comunità
print("\n=== GENERI DOMINANTI PER COMUNITÀ ===\n")

# Ottieni tutte le comunità presenti nel dataset completo
all_communities = sorted(df['modularity_class'].unique())

for community in all_communities:
    if community in heatmap_data.index:
        # Genere dominante
        top_genre = heatmap_data.loc[community].idxmax()
        top_count = heatmap_data.loc[community].max()
        total_count = heatmap_data.loc[community].sum()
        percentage = (top_count / total_count * 100) if total_count > 0 else 0
        
        # Top 3 artisti più popolari che hanno il genere dominante
        community_artists_with_genre = df_clean[
            (df_clean['modularity_class'] == community) & 
            (df_clean[genre_column].str.contains(top_genre, na=False, regex=False))
        ].nlargest(3, 'popularity')
        
        print(f"Comunità {community}:")
        print(f"  Genere dominante: {top_genre} ({top_count}/{int(total_count)} = {percentage:.1f}%)")
        print(f"  Top 3 artisti più popolari con genere '{top_genre}':")
        for idx, (_, artist) in enumerate(community_artists_with_genre.iterrows(), 1):
            genres_display = artist[genre_column] if pd.notna(artist[genre_column]) and artist[genre_column] else "N/A"
            print(f"    {idx}. {artist['name']} (pop: {artist['popularity']}, generi: {genres_display})")
    else:
        # Comunità senza generi mappati
        community_all_artists = df[df['modularity_class'] == community]
        num_artists = len(community_all_artists)
        top_artists = community_all_artists.nlargest(3, 'popularity')
        
        print(f"Comunità {community}:")
        print(f"  ⚠ Nessun genere mappato ({num_artists} artisti senza generi validi)")
        print(f"  Top 3 artisti della comunità:")
        for idx, (_, artist) in enumerate(top_artists.iterrows(), 1):
            original_genres = artist['genres'] if pd.notna(artist['genres']) and artist['genres'] else "N/A"
            print(f"    {idx}. {artist['name']} (pop: {artist['popularity']}, generi originali: {original_genres})")
    print()
