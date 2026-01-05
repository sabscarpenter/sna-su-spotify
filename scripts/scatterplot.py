# Script per creare uno scatterplot della popolarità tra artisti collaboranti

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Configurazione colori
gephi_cmap = LinearSegmentedColormap.from_list("gephi", ["#BF84F9", "#DC7AF2", "#FB71FF"])

# Caricamento dati nodi e archi
nodes_df = pd.read_csv('../data/new/grezzi/nodes.csv')
edges_df = pd.read_csv('../data/new/grezzi/edges.csv')

# Mappatura ID artista -> popolarità
popularity_map = dict(zip(nodes_df['id'], nodes_df['popularity']))

# Creazione dataset per il grafico
edge_popularity = []
for idx, row in edges_df.iterrows():
    source_id = row['source']
    target_id = row['target']
    if source_id in popularity_map and target_id in popularity_map:
        edge_popularity.append({
            'source_popularity': popularity_map[source_id],
            'target_popularity': popularity_map[target_id],
            'weight': row['weight']
        })

df_edges = pd.DataFrame(edge_popularity)

# Creazione figura
fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Scatterplot con dimensione e colore basati sul peso
scatter = ax.scatter(df_edges['source_popularity'], 
                     df_edges['target_popularity'],
                     alpha=0.4,
                     s=df_edges['weight'] * 15, 
                     c=df_edges['weight'],
                     cmap=gephi_cmap,
                     edgecolors='black',
                     linewidths=0.5,
                     zorder=3)

ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Diagonale di simmetria
ax.plot([0, 100], [0, 100], 
         color='#A947C7', linestyle='--', alpha=0.6, linewidth=2, 
         label='Diagonale (simmetria)', zorder=2)

# Formattazione
ax.set_xlabel('Popolarità Artista Source', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Popolarità Artista Target', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Scatterplot Popolarità tra Artisti', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, linestyle='--', color='gray', zorder=1)
ax.set_aspect('equal', adjustable='box')

cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
cbar.set_label('Numero di Collaborazioni', fontweight='bold')
ax.legend(loc='upper left', fontsize=10)

plt.tight_layout()
plt.savefig('../report/scatterplot.png', dpi=300, bbox_inches='tight')
plt.show()

# Calcolo e stampa correlazione
correlation = df_edges['source_popularity'].corr(df_edges['target_popularity'])
print(f"Correlazione popolarita: {correlation:.3f}")