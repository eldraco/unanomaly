clear Xval;
clear X;
clear yval;

arg_list = argv ();
filename = arg_list{1};
#filename = 'test3.csv';
wanted = str2double(arg_list{2});
#epsilon = str2double(arg_list{2});
#epsilon = 0.000000000000000000000001;

file = load(filename);
#file = dlmread('test.csv',',');
X = file(:,:);

# Solo si hay etiquetas
#yval = file(:,2);

%  Apply the same steps to the larger dataset
[mu sigma2] = estimateGaussian(X);

%  Training set 
p = multivariateGaussian(X, mu, sigma2);

%  Cross-validation set
pval = multivariateGaussian(X, mu, sigma2);

%  Find the best threshold
#[epsilon F1] = selectThreshold(yval, pval);

#fprintf('Best epsilon found using cross-validation: %e\n', epsilon);
#fprintf('Best F1 on Cross Validation Set:  %f\n', F1);

# Search for the epsilon to match the wanted amount of anomalies
epsilon = 0.001;
for k=1:35
    epsilon = epsilon/10.0;
    if wanted >= length(X(p < epsilon))
        break
    end
endfor

fprintf('# Outliers found: %d\n', sum(p < epsilon));

for i=1:size(X(p < epsilon,:))(1)
    %fprintf("%d %d\n",X(p < epsilon,:)(i,:));
    for j=1:size(X(p < epsilon,:))(2)
        printf('%d ',X(p < epsilon,:)(i,j));
    endfor
    printf('\n');
endfor



