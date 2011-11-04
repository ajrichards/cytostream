%% silhouette value unittest

x = [2,2,3,4,5,6,7,8,9,7,6];
y = [5,4,3,5,3,9,9,8,7,7,6];

scatter(x,y)
xlim([0,12]);
ylim([0,12]);

X = [x;y].'
X
cidx = kmeans(X, 2, 'distance', 'sqeuclid')
%s = silhouette(X, cidx, 'Euclidean')
s = silhouette(X, cidx)