function [] = create_graphs()

% This script generate the graphs for the evaluations

PROCESSED_PREFIX = './processed/stats-rt-';
PROCESSED_SUFFIX = '.dat';

mkdir('./img/');

data = {}; % stores the data for each router
% for each item in data, we have 3 rows: the number of import updates
% received, the number of import withdraws received and the number of
% import updates damped

% read data
for k=1:27
    filename = sprintf('%s%d%s',PROCESSED_PREFIX,k, PROCESSED_SUFFIX);
    data{k} = textread(filename,'','delimiter','\t');
end

% aggregate for all AS's (see eval-topo.ppt)
data_as{1} = data{1}+data{2};
data_as{2} = sum_as(data,3:7);
data_as{3} = sum_as(data,8:11);
data_as{4} = sum_as(data,12:14);
data_as{5} = sum_as(data,15:20);
data_as{6} = data{21}+data{22};
data_as{7} = data{23};
data_as{8} = data{24}+data{25};
data_as{9} = data{26};
data_as{10} = data{27};

% First graph : evolution of import updates received, for each 
% router. The sum over the whole network is also displayed
myplot(data_as,1,'import updates received');

% Second graph : evolution of import withdraws received, for each 
% router. The sum over the whole network is also displayed
myplot(data_as,2,'import withdraws received');

% First graph : evolution of dampened routes, for each 
% router. The sum over the whole network is also displayed
myplot(data_as,3,'dampened paths');

end

function [result] = sum_as(data, indices)
result=zeros(size(data{indices(1)}));
for k=indices
    result = result + data{k};
end

end

function [ ]= myplot(data, m, label)
% TODO: reduce end of data when it remains constant

time = 10*(1:length(data{1}));
cc=hsv(11);

figure(m);
hold on;
legends={};

% find order in which we have to display elements
% and total
total = zeros(size(data{1}));
order = zeros(11,1);

for k=1:10
    order(k) = max(data{k}(m,:)); 
    total = total+data{k};
end
order(11)=max(total(m,:));
data{11}=total;

[val indices] = sort(order,'descend');

for k=1:11
    plot(time,data{indices(k)}(m,:),'color',cc(k,:));
    ylabel(sprintf('Number of %s',label));
    xlabel('Time [s]');
    legends{k} = sprintf('AS %d',indices(k));
    title(sprintf('Evolution of %s',label));
end
legends{find(indices==11)}='Total network';
legend(legends,'Location','NorthEast');
hold off

img_name = sprintf('./img/%s.png',label);
saveas(gcf,img_name,'png');
end
