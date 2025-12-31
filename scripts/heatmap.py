import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Configurazione colori
gephi_palette = [
    "#845D95", "#FB71FF", "#F6B2FB", "#A947C7", 
    "#BF84F9", "#C1A2F8", "#F659F7", "#7F69C6", 
    "#9C5B9E", "#DC7AF2", "#F4C0F7", "#8E7AF2"
]
gephi_cmap = LinearSegmentedColormap.from_list("gephi", ["#FFFFFF", "#F4C0F7", "#BF84F9", "#A947C7", "#845D95"])

# Caricamento dati
try:
    df = pd.read_csv('../data/gephi/nodes_mapped.csv')
    genre_column = 'genres_mapped'
    print("✓ Usando generi mappati")
except FileNotFoundError:
    df = pd.read_csv('../data/gephi/nodes.csv')
    genre_column = 'genres'
    print("⚠ File mappato non trovato, usando generi originali")
    print("  Esegui prima: python map_genres.py")

df_clean = df[df[genre_column].notna()].copy()
df_clean = df_clean[df_clean[genre_column].str.len() > 0].copy()

# Elaborazione generi e matrice
genres_expanded = []
for idx, row in df_clean.iterrows():
    genres = row[genre_column].split(';')
    community = row['modularity_class']
    for genre in genres:
        genre = genre.strip()
        if genre:
            genres_expanded.append({
                'community': community,
                'genre': genre
            })

df_genres = pd.DataFrame(genres_expanded)
heatmap_data = pd.crosstab(df_genres['community'], df_genres['genre'])

all_communities = sorted(df['modularity_class'].unique())
heatmap_data = heatmap_data.reindex(all_communities, fill_value=0)
heatmap_data = heatmap_data.sort_index()

genre_counts = df_genres['genre'].value_counts()
num_genres = min(15, len(genre_counts))
top_genres = genre_counts.head(num_genres).index
heatmap_data_filtered = heatmap_data[top_genres]
heatmap_data_filtered = heatmap_data_filtered[sorted(heatmap_data_filtered.columns)]

community_totals = df_clean.groupby('modularity_class').size()
heatmap_data_percentage = heatmap_data_filtered.div(community_totals, axis=0) * 100

# Creazione grafico
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
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Genere Musicale', fontsize=12, fontweight='bold', labelpad=10)
plt.ylabel('Comunità', fontsize=12, fontweight='bold', labelpad=10)
plt.xticks(rotation=90, ha='center', fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()

plt.savefig('../report/heatmap.png', dpi=300, bbox_inches='tight')
print("Heatmap salvata in: ../report/heatmap.png")
plt.show()

# Statistiche
print("\n=== STATISTICHE OMOFILIA DI GENERE ===\n")
print(f"Numero totale di comunità: {df_clean['modularity_class'].nunique()}")
print(f"Numero totale di generi unici: {len(genre_counts)}")
print(f"\nTop 10 generi più comuni:")
print(genre_counts.head(10))

print("\n=== GENERI DOMINANTI PER COMUNITÀ ===\n")

all_communities = sorted(df['modularity_class'].unique())

for community in all_communities:
    if community in heatmap_data.index:
        top_genre = heatmap_data.loc[community].idxmax()
        top_count = heatmap_data.loc[community].max()
        total_count = heatmap_data.loc[community].sum()
        percentage = (top_count / total_count * 100) if total_count > 0 else 0
        
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
