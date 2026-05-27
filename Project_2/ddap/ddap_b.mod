param maxNode, >= 0, integer;
set Nodes := 1..maxNode;
param moduleCapacity > 0;
set Links;
param link_nodeA {Links} in Nodes;
param link_nodeZ {Links} in Nodes;
param link_moduleCost {Links} >= 0;
set Demands;
param demand_nodeA {Demands} in Nodes;
param demand_nodeZ {Demands} in Nodes;
param demand_volume {Demands} >= 0;
param demand_maxPath {Demands} >= 0;
set Paths {d in Demands} := 1..demand_maxPath[d];
set Demand_pathLinks {d in Demands, p in Paths[d]} within Links;

# ZMIENNE DECYZYJNE: u binarne (wybór ścieżki), y całkowite
var u {d in Demands, p in Paths[d]} binary;
var y {l in Links} integer >= 0;

# Wymuszenie wyboru dokładnie jednej ścieżki
subject to SinglePathChoice {d in Demands}:
    sum {p in Paths[d]} u[d,p] = 1;

# Pojemność liczy cały wolumen, jeśli ścieżka u[d,p] == 1
subject to LinkCapacity {l in Links}:
    sum {d in Demands, p in Paths[d] : l in Demand_pathLinks[d,p]} (u[d,p] * demand_volume[d]) <= y[l] * moduleCapacity;

minimize DDAP_obj:
    sum {l in Links} link_moduleCost[l] * y[l];
