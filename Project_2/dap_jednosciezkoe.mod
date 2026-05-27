param maxNode >= 0, integer;
set Nodes := 1..maxNode;
param moduleCapacity > 0;
set Links;
param link_nodeA {Links} in Nodes;
param link_nodeZ {Links} in Nodes;
param link_moduleCost {Links} >= 0;
param y {Links} >= 0;
set Demands;
param demand_nodeA {Demands} in Nodes;
param demand_nodeZ {Demands} in Nodes;
param demand_volume {Demands} >= 0;
param demand_maxPath {Demands} >= 0;
set Paths {d in Demands} := 1..demand_maxPath[d];
set Demand_pathLinks {d in Demands, p in Paths[d]} within Links;

var x {d in Demands, p in Paths[d]} integer >= 0;
# Dodajemy zmienną binarną
var u {d in Demands, p in Paths[d]} binary;

# Ograniczenie: DOKŁADNIE JEDNA ścieżka musi być wybrana dla każdego zapotrzebowania
subject to OnePathOnly {d in Demands}:
    sum {p in Paths[d]} u[d,p] = 1;

# Ograniczenie: wolumen idzie tylko wybraną ścieżką
subject to DemandFlow {d in Demands, p in Paths[d]}:
    x[d,p] = u[d,p] * demand_volume[d];

subject to LinkCapacity {l in Links}:
    sum {d in Demands, p in Paths[d] : l in Demand_pathLinks[d,p]}
        x[d,p] <= y[l] * moduleCapacity;

minimize Dummy_obj: 0;
