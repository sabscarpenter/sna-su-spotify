import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.sankey import Sankey

# Palette estratta da Gephi
gephi_palette = [
    "#845D95", "#FB71FF", "#F6B2FB", "#A947C7", 
    "#BF84F9", "#C1A2F8", "#F659F7", "#7F69C6", 
    "#9C5B9E", "#DC7AF2", "#F4C0F7", "#8E7AF2"
]

# Carica i dati delle nazionalità
print("Caricamento dati nazionalità...")
df_nationalities = pd.read_csv('../data/artisti-e-nazionalita.csv')

# Rimuovi artisti senza nazionalità, con errori o unknown
df_nationalities = df_nationalities[
    (df_nationalities['country'] != 'Unknown') & 
    (df_nationalities['country'] != 'Error') &
    (df_nationalities['country'].notna())
].copy()

# Carica gli edge (collaborazioni)
print("Caricamento collaborazioni...")
df_edges = pd.read_csv('../data/pesata/edges.csv')

# Merge per ottenere le nazionalità di source e target
df_edges_with_countries = df_edges.merge(
    df_nationalities[['spotify_id', 'country']], 
    left_on='source', 
    right_on='spotify_id', 
    how='inner'
).rename(columns={'country': 'source_country'})

df_edges_with_countries = df_edges_with_countries.merge(
    df_nationalities[['spotify_id', 'country']], 
    left_on='target', 
    right_on='spotify_id', 
    how='inner'
).rename(columns={'country': 'target_country'})

# Rimuovi self-loops (stessa nazionalità non è interessante per le interazioni)
# Commenta la riga sotto se vuoi includere anche le collaborazioni all'interno dello stesso paese
# df_edges_with_countries = df_edges_with_countries[df_edges_with_countries['source_country'] != df_edges_with_countries['target_country']]

# Conta le interazioni per coppia di paesi
country_interactions = df_edges_with_countries.groupby(
    ['source_country', 'target_country']
).size().reset_index(name='weight')

# Prendi solo i top N paesi per evitare un diagramma troppo affollato
top_n = 15
top_countries = df_nationalities['country'].value_counts().head(top_n).index.tolist()

# Filtra solo le interazioni tra i top paesi
country_interactions_filtered = country_interactions[
    (country_interactions['source_country'].isin(top_countries)) & 
    (country_interactions['target_country'].isin(top_countries))
]

# Per il chord diagram, assicurati che le interazioni siano simmetriche
# Somma source->target con target->source
interactions_symmetric = []
processed_pairs = set()

for _, row in country_interactions_filtered.iterrows():
    pair = tuple(sorted([row['source_country'], row['target_country']]))
    
    if pair not in processed_pairs:
        # Trova tutte le connessioni tra questi due paesi
        weight_forward = country_interactions_filtered[
            (country_interactions_filtered['source_country'] == pair[0]) & 
            (country_interactions_filtered['target_country'] == pair[1])
        ]['weight'].sum()
        
        weight_backward = country_interactions_filtered[
            (country_interactions_filtered['source_country'] == pair[1]) & 
            (country_interactions_filtered['target_country'] == pair[0])
        ]['weight'].sum()
        
        total_weight = weight_forward + weight_backward
        
        if total_weight > 0:
            interactions_symmetric.append({
                'source': pair[0],
                'target': pair[1],
                'value': total_weight
            })
        
        processed_pairs.add(pair)

df_chord = pd.DataFrame(interactions_symmetric)

# Filtra solo le interazioni significative (almeno 3 collaborazioni)
min_collaborations = 3
df_chord = df_chord[df_chord['value'] >= min_collaborations]

print(f"\n=== STATISTICHE ===")
print(f"Paesi inclusi: {len(top_countries)}")
print(f"Interazioni totali: {len(df_chord)}")
print(f"Collaborazioni totali: {df_chord['value'].sum()}")
print(f"\nPaesi più rappresentati:")
for i, country in enumerate(top_countries[:10], 1):
    count = len(df_nationalities[df_nationalities['country'] == country])
    print(f"  {i}. {country}: {count} artisti")

# Crea una matrice con cerchi (bubble matrix)
def create_bubble_matrix(df_chord, top_countries, gephi_palette):
    """Crea una matrice con cerchi che rappresentano le collaborazioni"""
    
    # Crea matrice di adiacenza
    countries = sorted(top_countries)
    n = len(countries)
    matrix = np.zeros((n, n))
    
    country_to_idx = {country: i for i, country in enumerate(countries)}
    
    # Riempi la matrice
    for _, row in df_chord.iterrows():
        if row['source'] in country_to_idx and row['target'] in country_to_idx:
            i = country_to_idx[row['source']]
            j = country_to_idx[row['target']]
            matrix[i, j] = row['value']
            matrix[j, i] = row['value']  # Simmetrica
    
    # Calcola le percentuali: per ogni riga (paese), dividi per il totale delle sue collaborazioni
    matrix_percentage = np.zeros((n, n))
    for i in range(n):
        row_total = matrix[i, :].sum()
        if row_total > 0:
            matrix_percentage[i, :] = (matrix[i, :] / row_total) * 100
    
    # Crea la figura
    fig, ax = plt.subplots(figsize=(16, 14))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Disegna i cerchi
    for i in range(n):
        for j in range(n):
            percentage = matrix_percentage[i, j]
            if percentage > 0:
                # Dimensione del cerchio proporzionale alla percentuale (0-100%)
                # Il raggio massimo è 0.4 per stare dentro la cella
                max_radius = 0.4
                radius = max_radius * np.sqrt(percentage / 100)
                
                # Colore basato sulla riga (paese source)
                color = gephi_palette[i % len(gephi_palette)]
                
                # Opacità basata sulla percentuale
                alpha = 0.3 + (percentage / 100) * 0.6
                
                # Disegna il cerchio
                circle = plt.Circle((j, n-1-i), radius=radius, 
                                   color=color, alpha=alpha, 
                                   edgecolor='white', linewidth=1.5)
                ax.add_patch(circle)
    
    # Configura gli assi
    ax.set_xlim(-0.5, n-0.5)
    ax.set_ylim(-0.5, n-0.5)
    ax.set_aspect('equal')
    
    # Etichette
    ax.set_xticks(range(n))
    ax.set_xticklabels(countries, rotation=90, ha='center', fontsize=10)
    ax.set_yticks(range(n))
    ax.set_yticklabels(countries[::-1], fontsize=10)
    
    # Griglia sottile
    ax.set_xticks([i-0.5 for i in range(n+1)], minor=True)
    ax.set_yticks([i-0.5 for i in range(n+1)], minor=True)
    ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5, alpha=0.3)
    
    # Titolo
    ax.text(0.5, 1.05, 'Matrice di Collaborazioni tra Nazionalità', 
            transform=ax.transAxes,
            ha='center', va='bottom', fontsize=18, fontweight='bold')
    ax.text(0.5, 1.02, '(dimensione cerchi = percentuale di collaborazioni per paese)', 
            transform=ax.transAxes,
            ha='center', va='bottom', fontsize=12, style='italic', color='gray')
    
    return fig, ax

# Genera il bubble matrix
fig, ax = create_bubble_matrix(df_chord, top_countries, gephi_palette)

# Salva il diagramma
print("\nGenerazione bubble matrix...")
plt.tight_layout()
plt.savefig('../report/bubble_matrix_nazionalita.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Bubble matrix salvato in: ../report/bubble_matrix_nazionalita.png")
plt.show()

# Stampa le interazioni più forti
print("\n=== TOP 10 INTERAZIONI TRA PAESI ===")
top_interactions = df_chord.nlargest(10, 'value')
for idx, row in top_interactions.iterrows():
    print(f"{row['source']} ↔ {row['target']}: {int(row['value'])} collaborazioni")

# Analisi di omofilia (collaborazioni all'interno dello stesso paese)
print("\n=== OMOFILIA PER PAESE ===")
same_country = df_edges_with_countries[
    df_edges_with_countries['source_country'] == df_edges_with_countries['target_country']
].groupby('source_country').size().reset_index(name='internal_collabs')

total_collabs = df_edges_with_countries.groupby('source_country').size().reset_index(name='total_collabs')
homophily = same_country.merge(total_collabs, on='source_country', how='right').fillna(0)
homophily['homophily_ratio'] = (homophily['internal_collabs'] / homophily['total_collabs'] * 100).round(1)
homophily = homophily[homophily['source_country'].isin(top_countries)]
homophily = homophily.sort_values('homophily_ratio', ascending=False)

print("\nPercentuale di collaborazioni interne per paese:")
for _, row in homophily.head(10).iterrows():
    print(f"  {row['source_country']}: {row['homophily_ratio']:.1f}% ({int(row['internal_collabs'])}/{int(row['total_collabs'])})")
