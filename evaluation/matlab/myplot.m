% TODO: different line styles for different curves

function [ ]= myplot(data, m, label,legend_label, mytitle, display_sum)
% data = struct containing all data
% m = row index to consider for each data item
% label = title of y axis
% legend_label = legend of label (before the number)
% mytitle = title of graph
% display_sum = boolean that controls if the sum also has to be displayed

if(~ exist('../img/','dir'))
    mkdir('../img/');
end

[first_index last_index] = find_boundaries(data,m);

time = 10*(1:(last_index-first_index+1));
cc=hsv(length(data)+1);

figure();
hold on;
legends={};


% find order in which we have to display elements
order = zeros(length(data),1);
for k=1:length(data)
    order(k) = max(data{k}(m,:)); 
end
    
if(display_sum)
    total = zeros(size(data{1}));
     for k=1:length(data)
        total = total+data{k};
     end
    order(length(data)+1)=max(total(m,:));
    data{length(data)+1}=total;
end

[val indices] = sort(order,'descend');

for k=1:(length(data))
    plot(time,data{indices(k)}(m,first_index:last_index),'color',cc(k,:));
    ylabel(label);
    xlabel('Time [s]');
    if(strcmp(legend_label,'Router 3')==1)
       legends{k} = legend_label; % special case for damping only
    else
     legends{k} = sprintf('%s %d',legend_label,indices(k));
    end
    title(mytitle);
end

if(display_sum)
    legends{find(indices==(length(data)))}='Total';
end

legend(legends,'Location','NorthWest');
hold off

img_name = sprintf('../img/%s.png',mytitle);
saveas(gcf,img_name,'png');
disp(sprintf('Image saved to %s',img_name));
end