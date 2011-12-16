function [first_index last_index] = find_boundaries(data,m)
% find start and end of data. start = given by router 3 (first non zero
% val) and end = when sum remains constant
firsts = zeros(1,length(data));
lasts = zeros(1,length(data));
for k=1:length(data)
    pos1 = find(data{k}(m,:)>0,1);
    if (isempty(pos1))
       firsts(k)=length(data{k}(m,:)); 
    else
       firsts(k)=pos1;
    end
    pos2 = find(data{k}(m,:)==max(data{k}(m,:)),1);
     if (isempty(pos2))
       lasts(k)=0; 
    else
       lasts(k)=pos2;
    end
end
first_index = min(firsts);
last_index = max(lasts);

end