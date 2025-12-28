import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Carica i dati
df = pd.read_csv('../data/gephi/nodes.csv')

# Rimuovi le righe con generi mancanti
df_clean = df[df['genres'].notna()].copy()

# Espandi i generi (ogni artista può avere più generi separati da ";")
genres_expanded = []
for idx, row in df_clean.iterrows():
    genres = row['genres'].split(';')
    community = row['Modularity Class']
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

# Ordina le comunità
heatmap_data = heatmap_data.sort_index()

# Seleziona solo i generi più comuni (per rendere la heatmap leggibile)
genre_counts = df_genres['genre'].value_counts()
top_genres = genre_counts.head(20).index
heatmap_data_filtered = heatmap_data[top_genres]

# Crea la heatmap
plt.figure(figsize=(16, 10))
sns.heatmap(heatmap_data_filtered, 
            annot=True, 
            fmt='d', 
            cmap='YlOrRd',
            cbar_kws={'label': 'Numero di artisti'},
            linewidths=0.5)

plt.title('Distribuzione dei Generi Musicali per Comunità\n(Analisi Omofilia di Genere)', 
          fontsize=16, pad=20)
plt.xlabel('Genere Musicale', fontsize=12)
plt.ylabel('Comunità (Modularity Class)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Salva la figura
plt.savefig('../report/heatmap_genre_homophily.png', dpi=300, bbox_inches='tight')
print("Heatmap salvata in: ../report/heatmap_genre_homophily.png")

# Mostra la heatmap
plt.show()

# Stampa statistiche aggiuntive
print("\n=== STATISTICHE OMOFILIA DI GENERE ===\n")
print(f"Numero totale di comunità: {df_clean['Modularity Class'].nunique()}")
print(f"Numero totale di generi unici: {len(genre_counts)}")
print(f"\nTop 10 generi più comuni:")
print(genre_counts.head(10))

# Calcola l'indice di concentrazione per ogni comunità
print("\n=== GENERI DOMINANTI PER COMUNITÀ ===\n")
for community in sorted(heatmap_data.index):
    top_genre = heatmap_data.loc[community].idxmax()
    top_count = heatmap_data.loc[community].max()
    total_count = heatmap_data.loc[community].sum()
    percentage = (top_count / total_count * 100) if total_count > 0 else 0
    print(f"Comunità {community}: {top_genre} ({top_count}/{int(total_count)} = {percentage:.1f}%)")
