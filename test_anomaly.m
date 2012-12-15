clear Xval;
clear X;
clear yval;

arg_list = argv ();
filename = arg_list{1};
epsilon = str2double(arg_list{2});

file = load(filename);
#file = dlmread('test.csv',',');
X = file(:,[1,2]);
#Xval = file(:,[53,55,56,59,63,67,68,69,70,71,72,74,75,76,78]);

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

# a mano si no hay etiquetas para evaluar...
#epsilon = 0.0001;

#fprintf('Best epsilon found using cross-validation: %e\n', epsilon);
#fprintf('Best F1 on Cross Validation Set:  %f\n', F1);
fprintf('# Outliers found: %d\n', sum(p < epsilon));
for i=1:length(X(p < epsilon,[1,2]))
    fprintf("%d %d\n",X(p < epsilon,:)(i,:));
endfor
