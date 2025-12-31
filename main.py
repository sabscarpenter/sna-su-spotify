import pandas as pd
import time
import os
from collections import Counter
from scripts.utils import get_spotify_client
from scripts.data_collection import get_artist_info, get_collaborations

MAX_DEPTH = 1

def load_seeds(filepath):
    seeds = []
    if not os.path.exists(filepath):
        print(f"Errore: il file {filepath} non esiste!")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 2:
                    seeds.append(parts[1].strip())
    return seeds

def main():
    sp = get_spotify_client()
    seeds = load_seeds('seeds.txt')
    
    nodes_data = {}
    edge_counts = Counter()
    processed_ids = set()
    current_level_queue = seeds

    print(f"Inizio raccolta dati con PROFONDITÀ: {MAX_DEPTH}")

    # Raccolta dati per livello
    for depth in range(MAX_DEPTH):
        print(f"\n--- ANALISI LIVELLO {depth + 1} ---")
        next_level_queue = []
        
        for artist_id in current_level_queue:
            if artist_id in processed_ids:
                continue
            
            try:
                if artist_id not in nodes_data:
                    info = get_artist_info(sp, artist_id)
                    info['genres'] = ';'.join(info['genres']) if info['genres'] else ""
                    nodes_data[artist_id] = info

                collabs = get_collaborations(sp, artist_id)
                print(f"[{depth+1}] Processato: {nodes_data[artist_id]['name']} ({len(collabs)} feat trovati)")
                
                for a, b in collabs:
                    pair = tuple(sorted((a, b)))
                    edge_counts[pair] += 1
                    
                    if a not in processed_ids: next_level_queue.append(a)
                    if b not in processed_ids: next_level_queue.append(b)
                
                processed_ids.add(artist_id)
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Errore con {artist_id}: {e}")

        current_level_queue = list(set(next_level_queue))
        if not current_level_queue:
            break

    # Recupero profili mancanti
    print("\nFase finale: Recupero profili mancanti...")
    
    all_discovered_ids = set()
    for (u, v) in edge_counts.keys():
        all_discovered_ids.add(u)
        all_discovered_ids.add(v)

    missing_ids = list(all_discovered_ids - set(nodes_data.keys()))
    if missing_ids:
        print(f"Scaricamento dati per {len(missing_ids)} collaboratori esterni...")
        for i in range(0, len(missing_ids), 50):
            batch = missing_ids[i:i+50]
            try:
                results = sp.artists(batch)
                for artist in results['artists']:
                    if artist:
                        nodes_data[artist['id']] = {
                            'id': artist['id'],
                            'name': artist['name'],
                            'popularity': artist['popularity'],
                            'genres': ';'.join(artist['genres']) if artist['genres'] else ""
                        }
                time.sleep(0.5)
            except Exception as e:
                print(f"Errore batch: {e}")

    # Salvataggio risultati
    if not os.path.exists('data'): os.makedirs('data')
    
    df_nodes = pd.DataFrame(list(nodes_data.values())).drop_duplicates(subset='id')
    
    edges_list = []
    for (u, v), w in edge_counts.items():
        edges_list.append({
            'source': u,
            'target': v,
            'weight': w
        })
    df_edges = pd.DataFrame(edges_list)

    df_nodes.to_csv('data/nodes.csv', index=False)
    df_edges.to_csv('data/edges.csv', index=False)
    
    print("-" * 30)
    print(f"FINE! Ora hai {len(df_nodes)} nodi e {len(df_edges)} archi pesati.")

if __name__ == "__main__":
    main()