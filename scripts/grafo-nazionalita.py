# Script per creare un grafo delle collaborazioni tra nazioni

import pandas as pd
from collections import defaultdict

# Percorsi dei file di input e output
INPUT_ARTISTI = r'c:\Users\itali\Documents\uni\social\spotify\data\new\nazioni\artisti-e-nazionalita.csv'
INPUT_EDGES = r'c:\Users\itali\Documents\uni\social\spotify\data\new\grezzi\edges.csv'
OUTPUT_NODES = r'c:\Users\itali\Documents\uni\social\spotify\data\new\nazioni\nodes.csv'
OUTPUT_EDGES = r'c:\Users\itali\Documents\uni\social\spotify\data\new\nazioni\edges.csv'


def crea_grafo_nazioni():
    """Crea un grafo con nazioni come nodi e collaborazioni internazionali come archi."""
    
    # Carica mapping artista -> nazionalità
    df_artisti = pd.read_csv(INPUT_ARTISTI)
    artista_nazione = dict(zip(df_artisti['spotify_id'], df_artisti['country']))
    
    # Carica edges tra artisti
    df_edges = pd.read_csv(INPUT_EDGES)
    
    # Conta collaborazioni tra nazioni
    collaborazioni_nazioni = defaultdict(int)
    
    for _, row in df_edges.iterrows():
        source_id = row['source']
        target_id = row['target']
        weight = row['weight']
        
        nazione_source = artista_nazione.get(source_id)
        nazione_target = artista_nazione.get(target_id)
        
        if (nazione_source and nazione_target and 
            nazione_source.lower() != 'unknown' and 
            nazione_target.lower() != 'unknown'):
            coppia = tuple(sorted([nazione_source, nazione_target]))
            collaborazioni_nazioni[coppia] += weight
    
    # Estrai nazioni uniche
    nazioni = set()
    for coppia in collaborazioni_nazioni.keys():
        nazioni.add(coppia[0])
        nazioni.add(coppia[1])
    
    # Crea CSV dei nodi
    df_nodes = pd.DataFrame({
        'Id': sorted(nazioni),
        'Label': sorted(nazioni)
    })
    df_nodes.to_csv(OUTPUT_NODES, index=False, encoding='utf-8-sig')
    
    # Crea CSV degli archi
    edges_data = []
    for (nazione1, nazione2), peso in collaborazioni_nazioni.items():
        edges_data.append({
            'Source': nazione1,
            'Target': nazione2,
            'Weight': peso,
            'Type': 'Undirected'
        })
    
    df_edges_output = pd.DataFrame(edges_data)
    df_edges_output = df_edges_output.sort_values('Weight', ascending=False)
    df_edges_output.to_csv(OUTPUT_EDGES, index=False, encoding='utf-8-sig')
    
    # Stampa statistiche finali
    print(f"Nazioni totali: {len(nazioni)}")
    print(f"Collaborazioni tra nazioni: {len(edges_data)}")
    print(f"Collaborazioni totali (peso): {df_edges_output['Weight'].sum()}")
    
    return df_nodes, df_edges_output


if __name__ == "__main__":
    print("Creazione grafo nazioni per Gephi")
    crea_grafo_nazioni()
    print("Completato")
