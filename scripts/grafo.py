import pandas as pd
from collections import defaultdict

# Percorsi dei file
INPUT_ARTISTI = r'c:\Users\itali\Documents\uni\social\spotify\data\grafo\artisti-e-nazionalita.csv'
INPUT_EDGES = r'c:\Users\itali\Documents\uni\social\spotify\data\pesata\edges.csv'
OUTPUT_NODES = r'c:\Users\itali\Documents\uni\social\spotify\data\grafo\nodes.csv'
OUTPUT_EDGES = r'c:\Users\itali\Documents\uni\social\spotify\data\grafo\edges.csv'

def crea_grafo_nazioni():
    """
    Crea un grafo con nazioni come nodi e collaborazioni internazionali come archi.
    """
    # 1. Carica mapping artista -> nazionalità
    print("Caricamento mapping artisti -> nazionalità...")
    df_artisti = pd.read_csv(INPUT_ARTISTI)
    artista_nazione = dict(zip(df_artisti['spotify_id'], df_artisti['country']))
    print(f"  ✓ {len(artista_nazione)} artisti caricati")
    
    # 2. Carica edges tra artisti
    print("\nCaricamento edges tra artisti...")
    df_edges = pd.read_csv(INPUT_EDGES)
    print(f"  ✓ {len(df_edges)} collegamenti caricati")
    
    # 3. Crea contatore per collaborazioni tra nazioni
    print("\nCalcolo collaborazioni tra nazioni...")
    collaborazioni_nazioni = defaultdict(int)
    edges_validi = 0
    edges_ignorati = 0
    
    for _, row in df_edges.iterrows():
        source_id = row['source']
        target_id = row['target']
        weight = row['weight']
        
        # Ottieni le nazioni dei due artisti
        nazione_source = artista_nazione.get(source_id)
        nazione_target = artista_nazione.get(target_id)
        
        # Se entrambe le nazioni sono note e non sono "Unknown"
        if (nazione_source and nazione_target and 
            nazione_source.lower() != 'unknown' and 
            nazione_target.lower() != 'unknown'):
            # Ordina le nazioni per evitare duplicati (A-B e B-A)
            # In questo modo (Italia, USA) e (USA, Italia) saranno la stessa coppia
            coppia = tuple(sorted([nazione_source, nazione_target]))
            
            # Aggiungi il peso (numero di collaborazioni)
            collaborazioni_nazioni[coppia] += weight
            edges_validi += 1
        else:
            edges_ignorati += 1
    
    print(f"  ✓ Edges processati: {edges_validi}")
    print(f"  ✓ Edges ignorati (artisti senza nazione): {edges_ignorati}")
    
    # 4. Estrai tutte le nazioni uniche
    print("\nEstrazione nazioni uniche...")
    nazioni = set()
    for coppia in collaborazioni_nazioni.keys():
        nazioni.add(coppia[0])
        nazioni.add(coppia[1])
    print(f"  ✓ {len(nazioni)} nazioni trovate")
    
    # 5. Crea CSV dei nodi (nazioni)
    print("\nCreazione file nodi...")
    df_nodes = pd.DataFrame({
        'Id': sorted(nazioni),
        'Label': sorted(nazioni)
    })
    df_nodes.to_csv(OUTPUT_NODES, index=False, encoding='utf-8-sig')
    print(f"  ✓ Salvato: {OUTPUT_NODES}")
    print(f"  ✓ {len(df_nodes)} nodi creati")
    
    # 6. Crea CSV degli archi (collaborazioni tra nazioni)
    print("\nCreazione file archi...")
    edges_data = []
    for (nazione1, nazione2), peso in collaborazioni_nazioni.items():
        edges_data.append({
            'Source': nazione1,
            'Target': nazione2,
            'Weight': peso,
            'Type': 'Undirected'  # Gephi riconosce questo campo
        })
    
    df_edges_output = pd.DataFrame(edges_data)
    # Ordina per peso decrescente
    df_edges_output = df_edges_output.sort_values('Weight', ascending=False)
    df_edges_output.to_csv(OUTPUT_EDGES, index=False, encoding='utf-8-sig')
    print(f"  ✓ Salvato: {OUTPUT_EDGES}")
    print(f"  ✓ {len(df_edges_output)} archi creati")
    
    # 7. Stampa statistiche
    print("\n" + "="*60)
    print("STATISTICHE")
    print("="*60)
    print(f"Nazioni totali: {len(nazioni)}")
    print(f"Collaborazioni tra nazioni: {len(edges_data)}")
    print(f"Collaborazioni totali (peso): {df_edges_output['Weight'].sum()}")
    print(f"Collaborazione più forte: {df_edges_output.iloc[0]['Source']} ↔ {df_edges_output.iloc[0]['Target']} ({df_edges_output.iloc[0]['Weight']} collaborazioni)")
    print("\nTop 10 collaborazioni:")
    for idx, row in df_edges_output.head(10).iterrows():
        print(f"  {row['Source']:30} ↔ {row['Target']:30} : {row['Weight']:4} collaborazioni")
    print("="*60)
    
    return df_nodes, df_edges_output

if __name__ == "__main__":
    print("="*60)
    print("CREAZIONE GRAFO NAZIONI PER GEPHI")
    print("="*60)
    crea_grafo_nazioni()
    print("\n✓ Completato! I file sono pronti per essere importati in Gephi.")
