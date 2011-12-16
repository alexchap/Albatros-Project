% aggregate stats for each AS according to topology

function [data_as] = aggregate_as(data)

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

end

function [result] = sum_as(data, indices)
result=zeros(size(data{indices(1)}));
for k=indices
    result = result + data{k};
end

end