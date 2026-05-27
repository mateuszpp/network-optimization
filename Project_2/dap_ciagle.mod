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

# Zmienna x JEST CIĄGŁA (brak slowa integer)
var x {d in Demands, p in Paths[d]} >= 0;

subject to DemandFlow {d in Demands}:
    sum {p in Paths[d]} x[d,p] = demand_volume[d];

subject to LinkCapacity {l in Links}:
    sum {d in Demands, p in Paths[d] : l in Demand_pathLinks[d,p]}
        x[d,p] <= y[l] * moduleCapacity;

minimize Dummy_obj: 0;
