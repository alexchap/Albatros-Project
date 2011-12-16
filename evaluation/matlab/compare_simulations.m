% compare two simulations and show the evolution of the difference 
% of the number of updates/withdraws between the two

% ASSUMPTION : simulation 2 has lower updates/withdraws !

data1 = get_data('../SIM1');
data2 = get_data('../SIM2');

data1_as = aggregate_as(data1);
data2_as = aggregate_as(data2);

% import updates received
diff = {};

for k=1:length(data1_as)
   
    for m=1:2
       [first1, last1] = find_boundaries(data1_as,m);
       [first2, last2] = find_boundaries(data2_as,m);
       first_index = min(first1,first2);
       last_index = min(last1,last2);
       diff{k}(m,:) = data1_as{k}(m,first_index:last_index) - data2_as{k}(m,first_index:last_index);
    end

end

mytitle1='Difference of import updates received between SIM1 and SIM2';
mytitle2='Difference of import withdraws received between SIM1 and SIM2';


myplot(diff,1,'Import updates received (SIM1 - SIM2)','AS ',mytitle1, 1);
myplot(diff,2,'Import withdraws received (SIM1 - SIM2)','AS ',mytitle2, 1);


