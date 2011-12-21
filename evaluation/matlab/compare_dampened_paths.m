% compare two simulations and show the evolution of the difference 
% of the number of updates/withdraws between the two

% ASSUMPTION : simulation 2 has lower updates/withdraws !

data1 = get_data('../EXP2');
data2 = get_data('../EXP3');

[first1, last1] = find_boundaries(data1,3);
[first2, last2] = find_boundaries(data2,3);
first_index = min(first1,first2);
last_index = min(last1,last2);

data_rt3_exp2 = data1{3}(3,first_index:last_index);
data_rt3_exp3 = data2{3}(3,first_index:last_index);


% import updates received
time = 10*(1:(last_index-first_index+1));

hold all;
plot(time,data_rt3_exp3,'-r',time,data_rt3_exp2,'--b');
xlabel('Time');
ylabel('Number of dampened paths');
mytitle='Evolution of dampened paths for experiments 2 and 3';
title(mytitle);
legend('Experiment 3','Experiment 2','Location','NorthWest');

img_name = sprintf('../img/%s.eps',mytitle);
saveas(gcf,img_name,'eps');
disp(sprintf('Image saved to %s',img_name));


hold off;
