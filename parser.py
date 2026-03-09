import re
from models import Link, Demand, Network

def parse_network_file(filepath):
    links = []
    demands = []
    module_capacity = 1
    
    with open(filepath, 'r') as file:
        lines = file.readlines()

    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if "param moduleCapacity" in line:
            match = re.search(r':=\s*(\d+)', line)
            if match:
                module_capacity = int(match.group(1))
            continue

        if line.startswith("param: Links:"):
            current_section = "LINKS"
            continue
        elif line.startswith("param: Demands:"):
            current_section = "DEMANDS"
            continue
        elif line.startswith(";"):
            current_section = None
            continue

        if current_section == "LINKS":
            parts = line.split()
            if len(parts) >= 4:
                links.append(Link(parts[0], parts[1], parts[2], parts[3]))
                
        elif current_section == "DEMANDS":
            parts = line.split()
            if len(parts) >= 4:
                demands.append(Demand(parts[0], parts[1], parts[2], parts[3]))
                
        # ZMIANA TUTAJ: Bardziej elastyczny warunek wyłapujący ścieżki
        elif line.startswith("set Demand") and "[" in line and ":=" in line:
            match = re.search(r'\[(\d+),(\d+)\]\s*:=\s*(.*?);', line)
            if match:
                d_id = int(match.group(1))
                path_links = [int(x) for x in match.group(3).split()]
                for d in demands:
                    if d.id == d_id:
                        d.paths.append(path_links)
                        break
                        
    return Network(links, demands, module_capacity)