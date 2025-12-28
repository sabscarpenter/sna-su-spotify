import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Carica i dati
nodes_df = pd.read_csv('../data/pesata/nodes.csv')
edges_df = pd.read_csv('../data/pesata/edges.csv')

# Crea un dizionario per mappare id -> popolarità
popularity_map = dict(zip(nodes_df['id'], nodes_df['popularity']))

# Per ogni edge, recupera la popolarità di source e target
edge_popularity = []
for idx, row in edges_df.iterrows():
    source_id = row['source']
    target_id = row['target']
    
    # Controlla se entrambi gli artisti hanno una popolarità
    if source_id in popularity_map and target_id in popularity_map:
        source_pop = popularity_map[source_id]
        target_pop = popularity_map[target_id]
        weight = row['weight']
        
        edge_popularity.append({
            'source_popularity': source_pop,
            'target_popularity': target_pop,
            'weight': weight
        })

# Crea DataFrame con le popolarità degli edge
df_edges = pd.DataFrame(edge_popularity)

print(f"Numero totale di collegamenti: {len(df_edges)}")
print(f"Range popolarità source: {df_edges['source_popularity'].min()} - {df_edges['source_popularity'].max()}")
print(f"Range popolarità target: {df_edges['target_popularity'].min()} - {df_edges['target_popularity'].max()}")

# Crea lo scatterplot
plt.figure(figsize=(12, 12))

# Plot con trasparenza per vedere le sovrapposizioni
# Usa il peso per dimensionare i punti
scatter = plt.scatter(df_edges['source_popularity'], 
                     df_edges['target_popularity'],
                     alpha=0.3,
                     s=df_edges['weight'] * 10,  # Dimensione proporzionale al peso
                     c=df_edges['weight'],
                     cmap='viridis',
                     edgecolors='black',
                     linewidths=0.5)

# Aggiungi la linea diagonale per evidenziare la simmetria
min_pop = min(df_edges['source_popularity'].min(), df_edges['target_popularity'].min())
max_pop = max(df_edges['source_popularity'].max(), df_edges['target_popularity'].max())
plt.plot([min_pop, max_pop], [min_pop, max_pop], 
         'r--', alpha=0.5, linewidth=2, label='Diagonale (simmetria)')

# Configurazione del grafico
plt.xlabel('Popolarità Artista Source', fontsize=14)
plt.ylabel('Popolarità Artista Target', fontsize=14)
plt.title('Scatterplot Collegamenti tra Artisti\n(basato sulla Popolarità)', 
          fontsize=16, pad=20)

# Aggiungi griglia
plt.grid(True, alpha=0.3, linestyle='--')

# Colorbar per il peso
cbar = plt.colorbar(scatter, label='Peso del collegamento')

# Legenda
plt.legend(loc='upper left', fontsize=10)

# Assicura che gli assi abbiano la stessa scala
plt.axis('equal')
plt.xlim(min_pop - 5, max_pop + 5)
plt.ylim(min_pop - 5, max_pop + 5)

plt.tight_layout()

# Salva la figura
plt.savefig('../report/scatterplot_popularity_connections.png', dpi=300, bbox_inches='tight')
print("\nScatterplot salvato in: ../report/scatterplot_popularity_connections.png")

# Mostra il grafico
plt.show()

# Statistiche aggiuntive
print("\n=== STATISTICHE COLLEGAMENTI ===\n")
print(f"Media popolarità source: {df_edges['source_popularity'].mean():.2f}")
print(f"Media popolarità target: {df_edges['target_popularity'].mean():.2f}")
print(f"Peso medio collegamenti: {df_edges['weight'].mean():.2f}")
print(f"Peso massimo: {df_edges['weight'].max()}")

# Analizza la correlazione
correlation = df_edges['source_popularity'].corr(df_edges['target_popularity'])
print(f"\nCorrelazione tra popolarità source e target: {correlation:.3f}")
print("(Una correlazione positiva indica tendenza a collegarsi con artisti di popolarità simile)")

# Conta collegamenti sopra e sotto la diagonale
above_diagonal = len(df_edges[df_edges['source_popularity'] < df_edges['target_popularity']])
below_diagonal = len(df_edges[df_edges['source_popularity'] > df_edges['target_popularity']])
on_diagonal = len(df_edges[df_edges['source_popularity'] == df_edges['target_popularity']])

print(f"\nPunti sopra la diagonale: {above_diagonal}")
print(f"Punti sotto la diagonale: {below_diagonal}")
print(f"Punti sulla diagonale: {on_diagonal}")
print("\n(I punti sono simmetrici rispetto alla diagonale)")
