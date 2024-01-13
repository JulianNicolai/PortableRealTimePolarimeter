% Polarization Simulation
close all
clear all
% RPM = 3840;  % [RPM]
RPM = 3648;  % [RPM]
cycles = 5;
integ_time = cycles * 60 / RPM;  % [s]
fps = 1/integ_time;
% cycles = RPM * integ_time / 60;
% cycles = 78;
N = 1562; % Number of points per cycle

samples = N * cycles;

samples_per_sec = N * RPM / 60;

Ts = 2*pi/N;

% Choose Ex and Ey Values at Random
Ex = rand(1);
Ey = sqrt(1 - Ex^2);
phi = rand(1) * 2*pi;
Ey = Ey * exp(1i*phi);

S0 = Ex * conj(Ex) + Ey * conj(Ey);
S1 = Ex * conj(Ex) - Ey * conj(Ey);
S2 = Ex * conj(Ey) + Ey * conj(Ex);
S3 = 1i * (Ex * conj(Ey) - Ey * conj(Ex));

theta = 0 : Ts : 2*pi*cycles - Ts;

Itheta = S0/2 + S1/4 + S3/2 * sin(2*theta) + S1/4 * cos(4*theta) + S2/4 * sin(4*theta);
IthetaNoise = awgn(Itheta, 30);

% data = Itheta;
data = IthetaNoise;

y = fft(data);
ymod = y(1:(cycles*N / 2 + 1)) / samples;
yscaled = [ymod(1), ymod(2:end) * 2];
yscaledabs = abs(yscaled);

w1 = round(1 + (2 * cycles));
w2 = round(1 + (4 * cycles));

A0 = yscaled(1);
A1 = yscaled(w1) + yscaled(w1+1) + yscaled(w1+2) + yscaled(w1-1) + yscaled(w1-2);
A2 = yscaled(w2) + yscaled(w2+1) + yscaled(w2+2) + yscaled(w2-1) + yscaled(w2-2);

S1_calc = real(A2) * 4;
S2_calc = imag(A2) * -4;
S3_calc = imag(A1) * -2;
S0_calc = 2*A0 - S1_calc/2;

% fs = 1/Ts;
% freq = (0:length(y)-1)*fs/length(y);
% fshift = (-samples/2 : samples/2-1)*(fs/samples);

% plot(theta, data)
% xlim([0 2*pi])

plot(yscaledabs)

% savedata = [theta.', Itheta.'];
% writematrix(savedata, 'data1.csv')

% loc = w1;
% rng = loc-30:1:loc+30;
% comet3(real(yscaled(rng)), imag(yscaled(rng)), rng)
% xlabel("Real")
% ylabel("Imag")
% zlabel("Frequency")

% plot(fshift, yshiftabs)
% plot(y(1:(cycles*N / 2 + 1))/samples)
% xlim([0 1])
% plot(yshift / samples)



% % Now do the reverse to extract the parameters
% % Lets adjust the above curve through a moving average to make it "look" like measure data
% SimData = movmean(Itheta, 5);
% 
% x0 = [1 1 0 0];  % Set parameters to start from
% fit = @(b, theta) (2*b(1) + b(2))/4 + b(4)/2 * sin(2*theta) + b(2)/4 * cos(4*theta) + b(3)/4 * sin(4*theta);
% fcn = @(b) sum((fit(b, theta) - SimData).^2);  % Least-Squares cost function
% % s = fminsearch(fcn, [yr;  per;  -1;  ym])   
% 
% % Fitted Polarization Parameters
% s = fminsearch(fcn, x0);
% 
% Itheta_fit = (2*s(1) + s(2))/4 + s(4)/2 * sin(2*theta) + s(2)/4 * cos(4*theta) + s(3)/4 * sin(4*theta);

% Apply FFT


% % Compare the data sets
% figure(2)
% hold on
% plot(theta, Itheta, '-b', 'LineWidth', 1)
% plot(theta, SimData, '.k', 'MarkerSize', 10)
% plot(theta, Itheta_fit, '.--r', 'LineWidth', 1)
% hold off