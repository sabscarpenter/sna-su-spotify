import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Configurazione colori
gephi_palette = [
    "#845D95", "#FB71FF", "#F6B2FB", "#A947C7", 
    "#BF84F9", "#C1A2F8", "#F659F7", "#7F69C6", 
    "#9C5B9E", "#DC7AF2", "#F4C0F7", "#8E7AF2"
]
gephi_cmap = LinearSegmentedColormap.from_list("gephi", ["#BF84F9", "#DC7AF2", "#FB71FF"])

# Caricamento dati
nodes_df = pd.read_csv('../data/pesata/nodes.csv')
edges_df = pd.read_csv('../data/pesata/edges.csv')
artists_countries = pd.read_csv('../data/artisti-e-nazionalita.csv')

country_map = dict(zip(artists_countries['spotify_id'], artists_countries['country']))
nodes_df['country'] = nodes_df['id'].map(country_map)
nodes_df = nodes_df.dropna(subset=['country'])

print(f"Numero artisti con paese: {len(nodes_df)}")
print(f"Numero paesi unici: {nodes_df['country'].nunique()}\n")

id_to_country = dict(zip(nodes_df['id'], nodes_df['country']))

edge_countries = []
for idx, row in edges_df.iterrows():
    source_id = row['source']
    target_id = row['target']
    
    if source_id in id_to_country and target_id in id_to_country:
        source_country = id_to_country[source_id]
        target_country = id_to_country[target_id]
        weight = row['weight']
        
        edge_countries.append({
            'source_country': source_country,
            'target_country': target_country,
            'source_id': source_id,
            'target_id': target_id,
            'weight': weight
        })

df_edges = pd.DataFrame(edge_countries)

print(f"Numero collegamenti tra artisti con paese: {len(df_edges)}\n")

# Calcolo matrice di collaborazioni
artists_per_country = nodes_df['country'].value_counts().to_dict()
countries = sorted(list(set(df_edges['source_country'].unique()) | 
                       set(df_edges['target_country'].unique())))

min_artists = 10
countries = [c for c in countries if c != 'Unknown' and (artists_per_country.get(c, 0) >= min_artists or c == 'Italia')]

print(f"Nazioni selezionate (min {min_artists} artisti, escluso Unknown): {len(countries)}")
print(f"Nazioni: {', '.join(countries)}\n")

matrix = pd.DataFrame(0.0, index=countries, columns=countries)
matrix_counts = pd.DataFrame(0, index=countries, columns=countries)

for source_country in countries:
    artists_from_source = set(nodes_df[nodes_df['country'] == source_country]['id'])
    total_artists_source = len(artists_from_source)
    
    for target_country in countries:
        collabs = df_edges[
            (df_edges['source_country'] == source_country) & 
            (df_edges['target_country'] == target_country)
        ]
        
        unique_source_artists = collabs['source_id'].nunique()
        
        if total_artists_source > 0:
            percentage = (unique_source_artists / total_artists_source) * 100
            matrix.loc[source_country, target_country] = percentage
            matrix_counts.loc[source_country, target_country] = unique_source_artists

print("=== MATRICE PERCENTUALI ===")
print(matrix.round(1))
print("\n=== MATRICE CONTEGGI ===")
print(matrix_counts)

# Creazione grafico
fig, ax = plt.subplots(figsize=(14, 12))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

x_positions = []
y_positions = []
sizes = []
colors_values = []

for i, source_country in enumerate(countries):
    for j, target_country in enumerate(countries):
        percentage = matrix.loc[source_country, target_country]
        if percentage > 0:
            x_positions.append(i)
            y_positions.append(j)
            sizes.append(percentage * 50)
            colors_values.append(percentage)

scatter = ax.scatter(x_positions, y_positions,
                    s=sizes,
                    c=colors_values,
                    cmap=gephi_cmap,
                    alpha=0.6,
                    edgecolors='black',
                    linewidths=1,
                    vmin=0,
                    vmax=100)

ax.set_xticks(range(len(countries)))
ax.set_yticks(range(len(countries)))
ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=10)
ax.set_yticklabels(countries, fontsize=10)
ax.grid(True, alpha=0.3, linestyle='--', color='gray', zorder=0)

ax.set_xlabel('Nazione Artisti Source', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Nazione Artisti Target', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Collaborazioni tra Nazioni\n(% di artisti di una nazione che collaborano con artisti di un\'altra)', 
            fontsize=16, fontweight='bold', pad=20)

cbar = plt.colorbar(scatter, ax=ax, label='Percentuale di Collaborazione (%)')
cbar.ax.tick_params(labelsize=10)

ax.plot([-0.5, len(countries)-0.5], [-0.5, len(countries)-0.5], 
        color='#A947C7', linestyle='--', alpha=0.6, linewidth=2, 
        label='Diagonale (collaborazioni interne)', zorder=1)

ax.legend(loc='upper right', fontsize=10)
ax.set_xlim(-0.5, len(countries)-0.5)
ax.set_ylim(-0.5, len(countries)-0.5)

plt.tight_layout()
plt.savefig('../report/bubble.png', dpi=300, bbox_inches='tight')
print("\n✓ Bubble salvata in: ../report/bubble.png")
plt.show()

# Statistiche
print("\n=== STATISTICHE COLLABORAZIONI TRA NAZIONI ===\n")

matrix_flat = []
for source in countries:
    for target in countries:
        if source != target:
            percentage = matrix.loc[source, target]
            count = matrix_counts.loc[source, target]
            if percentage > 0:
                matrix_flat.append({
                    'source': source,
                    'target': target,
                    'percentage': percentage,
                    'count': count
                })

df_flat = pd.DataFrame(matrix_flat).sort_values('percentage', ascending=False)

print("Top 10 collaborazioni (% artisti source → target):\n")
for idx, row in df_flat.head(10).iterrows():
    print(f"{row['source']:25} → {row['target']:25}: {row['percentage']:5.1f}% ({int(row['count'])} artisti)")

print("\n\nCollaborazioni intra-nazionali (artisti dello stesso paese):\n")
for country in countries:
    percentage = matrix.loc[country, country]
    count = matrix_counts.loc[country, country]
    total_artists = artists_per_country[country]
    if percentage > 0:
        print(f"{country:25}: {percentage:5.1f}% ({int(count)}/{total_artists} artisti)")

avg_inter = df_flat['percentage'].mean()
print(f"\nMedia percentuale collaborazioni inter-nazionali: {avg_inter:.2f}%")

diag_values = [matrix.loc[c, c] for c in countries if matrix.loc[c, c] > 0]
if diag_values:
    avg_intra = np.mean(diag_values)
    print(f"Media percentuale collaborazioni intra-nazionali: {avg_intra:.2f}%")
