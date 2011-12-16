function [ data ] = get_data( directory )
PROCESSED_PREFIX = sprintf('%s/stats-rt-',directory);
PROCESSED_SUFFIX = '.dat';

data = {}; % stores the data for each router
% for each item in data, we have 3 rows: the number of import updates
% received, the number of import withdraws received and the number of
% import updates damped

% read data
for k=1:27
    filename = sprintf('%s%d%s',PROCESSED_PREFIX,k, PROCESSED_SUFFIX);
    data{k} = textread(filename,'','delimiter','\t');
end


end

