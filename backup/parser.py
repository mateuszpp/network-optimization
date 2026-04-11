import re
from models import Link, Demand, Network

def parse_network_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Usunięcie ewentualnych komentarzy (# do końca linii)
    content = re.sub(r'#.*', '', content)
        
    # 1. moduleCapacity
    mod_cap_match = re.search(r'moduleCapacity\s*:=\s*(\d+)', content)
    module_capacity = int(mod_cap_match.group(1)) if mod_cap_match else 1
    
    # 2. Parsowanie Links
    links = []
    # re.DOTALL pozwala znakowi '.' dopasować się również do znaków nowej linii (\n)
    links_block = re.search(r'param:\s*Links:.*?[:=]+\s*(.*?)\s*;', content, re.DOTALL)
    if links_block:
        tokens = links_block.group(1).split()
        # Bierzemy paczki po 4 tokeny (id, nodeA, nodeZ, capacity/cost)
        for i in range(0, len(tokens), 4):
            if i + 3 < len(tokens):
                links.append(Link(tokens[i], tokens[i+1], tokens[i+2], tokens[i+3]))
                
    # 3. Parsowanie Demands (z inteligentnym wykrywaniem kolumny Volume)
    demands = []
    volume_idx = 4 # Domyślnie 5. element (indeks 4)
    
    # Wyciąganie nagłówka, by zlokalizować demand_volume
    header_match = re.search(r'param:\s*Demands:(.*?)[:=]+', content, re.DOTALL)
    if header_match:
        header_tokens = header_match.group(1).replace(',', ' ').split()
        if 'demand_volume' in header_tokens:
            # +1, ponieważ token 0 to zawsze ID zapotrzebowania, którego nie ma w nagłówku
            volume_idx = header_tokens.index('demand_volume') + 1

    demands_block = re.search(r'param:\s*Demands:.*?[:=]+\s*(.*?)\s*;', content, re.DOTALL)
    if demands_block:
        tokens = demands_block.group(1).split()
        # Bierzemy paczki po 5 tokenów (id, nodeA, nodeZ, kolumna4, kolumna5)
        for i in range(0, len(tokens), 5):
            if i + 4 < len(tokens):
                d_id = tokens[i]
                d_a = tokens[i+1]
                d_z = tokens[i+2]
                d_vol = tokens[i + volume_idx] # Używamy sprytnego indeksu!
                demands.append(Demand(d_id, d_a, d_z, d_vol))
                
    # 4. Parsowanie Ścieżek (odporne na spacje, nowelinie i różne nazwy)
    # Wyłapuje: set DemandPath_links [ 1 , 1 ] := 1 5 ;
    # Jak i:    set Demand_pathLinks[1,1] := 1 5;
    path_regex = r'set\s+Demand(?:Path_links|_pathLinks)\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]\s*:=\s*(.*?)\s*;'
    path_matches = re.finditer(path_regex, content)
    
    for match in path_matches:
        d_id = int(match.group(1))
        # Zabezpieczenie przed dziwnymi znakami na końcu
        path_string = match.group(3).strip() 
        path_links = [int(x) for x in path_string.split()]
        
        # Przypisanie ścieżki do odpowiedniego zapotrzebowania
        for d in demands:
            if d.id == d_id:
                d.paths.append(path_links)
                break
                
    return Network(links, demands, module_capacity)