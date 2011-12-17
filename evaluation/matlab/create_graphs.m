% This script generate the graphs for the evaluations


for k=1:3
    
mytitle1 = sprintf('SIM%d evolution of import updates received',k);
mytitle2 = sprintf('SIM%d evolution of import withdraws received',k);
mytitle3 = sprintf('SIM%d evolution of dampened paths',k);

data = get_data(sprintf('../SIM%d',k));

% aggregate for all AS's (see eval-topo.ppt)
data_as = aggregate_as(data);

% First graph : evolution of import updates received, for each 
% router. The sum over the whole network is also displayed
myplot(data_as,1,'Number of import updates received','AS ',mytitle1,0);

% Second graph : evolution of import withdraws received, for each 
% router. The sum over the whole network is also displayed
myplot(data_as,2,'Number of import withdraws received','AS ',mytitle2, 0);

% First graph : evolution of dampened routes, for each 
% router. The sum over the whole network is also displayed
dampened_paths{1} = data_as{2}; % router 3 is located in AS2
myplot(dampened_paths,3,'Number of dampened paths','Router 3',mytitle3,0);


end