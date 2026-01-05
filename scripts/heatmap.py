# Script per generare una heatmap della distribuzione dei generi per comunità

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
    df = pd.read_csv('../data/new/generi-mappati.csv')
    genre_column = 'genres_mapped'
except FileNotFoundError:
    df = pd.read_csv('../data/new/grezzi/nodes.csv')
    genre_column = 'genres'

df_clean = df[df[genre_column].notna()].copy()
df_clean = df_clean[df_clean[genre_column].str.len() > 0].copy()

# Filtro comunità da escludere
df_clean = df_clean[~df_clean['modularity_class'].isin([7, 11, 13, 14, 15, 16])].copy()

# Elaborazione generi e creazione matrice
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

all_communities = sorted(df_clean['modularity_class'].unique())
heatmap_data = heatmap_data.reindex(all_communities, fill_value=0)
heatmap_data = heatmap_data.sort_index()

# Selezione top generi
genre_counts = df_genres['genre'].value_counts()
num_genres = min(15, len(genre_counts))
top_genres = genre_counts.head(num_genres).index
heatmap_data_filtered = heatmap_data[top_genres]
heatmap_data_filtered = heatmap_data_filtered[sorted(heatmap_data_filtered.columns)]

# Calcolo percentuali
community_totals = df_clean.groupby('modularity_class').size()
heatmap_data_percentage = heatmap_data_filtered.div(community_totals, axis=0) * 100

# Creazione mappatura comunità -> artista più popolare del genere dominante
community_names = {}
for community in heatmap_data_percentage.index:
    dominant_genre = heatmap_data_percentage.loc[community].idxmax()
    community_artists = df_clean[
        (df_clean['modularity_class'] == community) & 
        (df_clean[genre_column].str.contains(dominant_genre, na=False, regex=False))
    ]
    if len(community_artists) > 0:
        top_artist = community_artists.nlargest(1, 'popularity').iloc[0]
        community_names[community] = f"comunità di {top_artist['name']}"

heatmap_data_percentage.rename(index=community_names, inplace=True)

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

plt.title('Distribuzione dei Generi Musicali per Comunità', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Genere Musicale', fontsize=12, fontweight='bold', labelpad=10)
plt.ylabel('Comunità', fontsize=12, fontweight='bold', labelpad=10)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)
plt.tight_layout()

plt.savefig('../report/heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

# Statistiche principali
print(f"Numero totale di comunita: {df_clean['modularity_class'].nunique()}")
print(f"Numero totale di generi unici: {len(genre_counts)}")
