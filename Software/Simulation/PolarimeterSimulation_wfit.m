%Polarization Simulation
close all
clear all
N=50; %Number of points

%Choose Ex and Ey Values at Random

Ex=rand(1);
Ey=sqrt(1-Ex^2);
phi=rand(1)*2*pi;
Ey=Ey*exp(1i*phi);


S0=Ex*conj(Ex)+Ey*conj(Ey)
S1=Ex*conj(Ex)-Ey*conj(Ey)
S2=Ex*conj(Ey)+Ey*conj(Ex)
S3=1i*(Ex*conj(Ey)-Ey*conj(Ex))

theta=linspace(0,2*pi,N)';

Itheta=(2*S0+S1)/4+S3/2*sin(2*theta)+S1/4*cos(4*theta)+S2/4*sin(4*theta);

figure
plot(theta,Itheta)

%Now do the reverse to extract the parameters
%Lets adjust the above curve through a moving average to make it "look" like measure data
SimData = movmean(Itheta,5);

x0=[1 1 0 0]; %set parameters to start from
fit = @(b,theta)  (2*b(1)+b(2))/4+b(4)/2*sin(2*theta)+b(2)/4*cos(4*theta)+b(3)/4*sin(4*theta);
fcn = @(b) sum((fit(b,theta) - SimData).^2);                              % Least-Squares cost function
% s = fminsearch(fcn, [yr;  per;  -1;  ym])   

%Fitted Polarization Parameters
s = fminsearch(fcn,x0)

Itheta_fit=(2*s(1)+s(2))/4+s(4)/2*sin(2*theta)+s(2)/4*cos(4*theta)+s(3)/4*sin(4*theta);

%Compare the data sets
figure(2)
hold on
plot(theta,Itheta,'-b','LineWidth',1)
plot(theta,SimData,'.k','MarkerSize',10)
plot(theta,Itheta_fit,'.--r','LineWidth',1)
hold off