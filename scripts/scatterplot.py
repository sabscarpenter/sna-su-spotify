import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Configurazione colori
gephi_palette = [
    "#845D95", "#FB71FF", "#F6B2FB", "#A947C7", 
    "#BF84F9", "#C1A2F8", "#F659F7", "#7F69C6", 
    "#9C5B9E", "#DC7AF2", "#F4C0F7", "#8E7AF2"
]
gephi_cmap = LinearSegmentedColormap.from_list("gephi", ["#BF84F9", "#DC7AF2", "#FB71FF"])

# Caricamento dati e preparazione
nodes_df = pd.read_csv('../data/pesata/nodes.csv')
edges_df = pd.read_csv('../data/pesata/edges.csv')

popularity_map = dict(zip(nodes_df['id'], nodes_df['popularity']))

edge_popularity = []
for idx, row in edges_df.iterrows():
    source_id = row['source']
    target_id = row['target']
    
    if source_id in popularity_map and target_id in popularity_map:
        source_pop = popularity_map[source_id]
        target_pop = popularity_map[target_id]
        weight = row['weight']
        
        edge_popularity.append({
            'source_popularity': source_pop,
            'target_popularity': target_pop,
            'weight': weight
        })

df_edges = pd.DataFrame(edge_popularity)

print(f"Numero totale di collegamenti: {len(df_edges)}")
print(f"Range popolarità source: {df_edges['source_popularity'].min()} - {df_edges['source_popularity'].max()}")
print(f"Range popolarità target: {df_edges['target_popularity'].min()} - {df_edges['target_popularity'].max()}")

# Creazione grafico
fig, ax = plt.subplots(figsize=(12, 12))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

scatter = ax.scatter(df_edges['source_popularity'], 
                     df_edges['target_popularity'],
                     alpha=0.4,
                     s=df_edges['weight'] * 10,
                     c=df_edges['weight'],
                     cmap=gephi_cmap,
                     edgecolors='black',
                     linewidths=0.5)

min_pop = min(df_edges['source_popularity'].min(), df_edges['target_popularity'].min())
max_pop = max(df_edges['source_popularity'].max(), df_edges['target_popularity'].max())
ax.plot([min_pop, max_pop], [min_pop, max_pop], 
         color='#A947C7', linestyle='--', alpha=0.6, linewidth=2, label='Diagonale (simmetria)')

ax.set_xlabel('Popolarità Artista Source', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Popolarità Artista Target', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Scatterplot Collegamenti tra Artisti\n(basato sulla Popolarità)', 
          fontsize=16, fontweight='bold', pad=20)
ax.tick_params(axis='both', labelsize=10)
ax.grid(True, alpha=0.3, linestyle='--', color='gray')

cbar = plt.colorbar(scatter, ax=ax, label='Numero di Collaborazioni')
ax.legend(loc='upper left', fontsize=10)

ax.axis('equal')
ax.set_xlim(min_pop - 5, max_pop + 5)
ax.set_ylim(min_pop - 5, max_pop + 5)

plt.tight_layout()
plt.savefig('../report/scatterplot.png', dpi=300, bbox_inches='tight')
print("\nScatterplot salvato in: ../report/scatterplot.png")
plt.show()

# Statistiche
print("\n=== STATISTICHE COLLEGAMENTI ===\n")
print(f"Media popolarità source: {df_edges['source_popularity'].mean():.2f}")
print(f"Media popolarità target: {df_edges['target_popularity'].mean():.2f}")
print(f"Peso medio collegamenti: {df_edges['weight'].mean():.2f}")
print(f"Peso massimo: {df_edges['weight'].max()}")

correlation = df_edges['source_popularity'].corr(df_edges['target_popularity'])
print(f"\nCorrelazione tra popolarità source e target: {correlation:.3f}")
print("(Una correlazione positiva indica tendenza a collegarsi con artisti di popolarità simile)")

above_diagonal = len(df_edges[df_edges['source_popularity'] < df_edges['target_popularity']])
below_diagonal = len(df_edges[df_edges['source_popularity'] > df_edges['target_popularity']])
on_diagonal = len(df_edges[df_edges['source_popularity'] == df_edges['target_popularity']])

print(f"\nPunti sopra la diagonale: {above_diagonal}")
print(f"Punti sotto la diagonale: {below_diagonal}")
print(f"Punti sulla diagonale: {on_diagonal}")
print("\n(I punti sono simmetrici rispetto alla diagonale)")
