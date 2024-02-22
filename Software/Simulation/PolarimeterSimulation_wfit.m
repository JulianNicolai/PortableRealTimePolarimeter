% Polarization Simulation
close all
% clear all
RPM = 3840;  % [RPM] max
cycles_per_sec = RPM / 60;  % [Hz]
samples_per_sec = 100e3;  % Samples per second
cycles = 5; % Number of cycles

samples_per_cycle = samples_per_sec / cycles_per_sec;  % Samples per cycle

integ_time = cycles / cycles_per_sec;  % [s]
fps = 1/integ_time;

SNR = 10;

Ts = 2*pi/samples_per_cycle;

theta = 0 : Ts : 2*pi*cycles - Ts;

% Choose Ex and Ey Values at Random
% Ex = rand(1);
% Ey = sqrt(1 - Ex^2);
% phi = rand(1) * 2*pi;
% Ey = Ey * exp(1i*phi);

S0 = Ex * conj(Ex) + Ey * conj(Ey);
S1 = Ex * conj(Ex) - Ey * conj(Ey);
S2 = Ex * conj(Ey) + Ey * conj(Ex);
S3 = 1i * (Ex * conj(Ey) - Ey * conj(Ex));

Itheta = S0/2 + S1/4 + S3/2 * sin(2*theta) + S1/4 * cos(4*theta) + S2/4 * sin(4*theta);
IthetaNoise = awgn(Itheta, SNR);

% data = Itheta;
data = IthetaNoise;


samples = length(data);
cycles_corr = samples / samples_per_sec * cycles_per_sec;
cycles = cycles_corr;

CORRECTION_FACTOR = 2.0;
w = hann(length(data)).' * CORRECTION_FACTOR;

data_op = data(1:end) .* w;

y = fft(data_op);
ymod = y(1:round(samples / 2)) / samples;
yscaled = [ymod(1), ymod(2:end) * 2];
yscaledabs = abs(yscaled);

w1 = 1 + (2 * cycles);
w2 = 1 + (4 * cycles);

A0 = yscaled(1);
A1 = yscaled(round(w1));
A2 = yscaled(round(w2));

S1_calc = real(A2) * 4;
S2_calc = imag(A2) * -4;
S3_calc = imag(A1) * -2;
S0_calc = 2*A0 - S1_calc/2;

% hold on
% plot(yscaledabs(1:50))
% xline(w1)
% xline(w2)
% 
% 
% 
% for i = 1:1:780
%     data_err = data(1:end - i);
%     
%     samples = length(data_err);
%     cycles_corr = samples / samples_per_cycle; 
%     cycles = cycles_corr;
% 
%     CORRECTION_FACTOR = 2.0;
%     w = hann(length(data_err)).' * CORRECTION_FACTOR;
% 
%     data_op = data_err(1:end) .* w;
% 
%     y = fft(data_op);
%     ymod = y(1:round(samples / 2)) / samples;
%     yscaled = [ymod(1), ymod(2:end) * 2];
%     yscaledabs = abs(yscaled);
% 
%     w1 = 1 + (2 * cycles);
%     w2 = 1 + (4 * cycles);
% 
%     A0 = yscaled(1);
%     A1 = yscaled(round(w1));
%     A2 = yscaled(round(w2));
% 
%     S1_calc = real(A2) * 4;
%     S2_calc = imag(A2) * -4;
%     S3_calc = imag(A1) * -2;
%     S0_calc = 2*A0 - S1_calc/2;
% 
%     plot(yscaledabs(1:50))
%     
% end
% 
% xline(w1)
% xline(w2)
% 
% hold off

% plot3(real(yscaled(1:100)), imag(yscaled(1:100)), 1:100)
% hold on
% plot3(real(yscaled1(1:100)), imag(yscaled1(1:100)), 1:100)
% hold off

% results = zeros(300, 5);
% 
% CORRECTION_FACTOR = 2.0;
% 
% for i = 1:5
%     w = hann(length(data)-i+1);
%     
%     operate_data = data(1:end-i+1) .* w;
%     
%     y = fft(operate_data);
%     y = y * CORRECTION_FACTOR;
%     ymod = y(1:round(cycles*N / 2 + 1)) / (samples-i+1);
%     yscaled = [ymod(1), ymod(2:end) * 2];
%     yscaledabs = abs(yscaled);
% 
%     w1 = round(1 + (2 * cycles));
%     w2 = round(1 + (4 * cycles));
% 
%     A0 = yscaled(1);
%     A1 = yscaled(w1) + yscaled(w1+1) + yscaled(w1+2) + yscaled(w1-1) + yscaled(w1-2);
%     A2 = yscaled(w2) + yscaled(w2+1) + yscaled(w2+2) + yscaled(w2-1) + yscaled(w2-2);
% 
%     S1_calc = real(A2) * 4;
%     S2_calc = imag(A2) * -4;
%     S3_calc = imag(A1) * -2;
%     S0_calc = 2*A0 - S1_calc/2;
%     results(i, :) = [i, S0_calc, S1_calc, S2_calc, S3_calc];
%     disp(i)
% end
% 
% hold on
% plot(results(:, 1), results(:, 2))
% plot(results(:, 1), results(:, 3))
% plot(results(:, 1), results(:, 4))
% plot(results(:, 1), results(:, 5))
% hold off
% yline(S0, '-', 'S0')
% yline(S1, '-', 'S1')
% yline(S2, '-', 'S2')
% yline(S3, '-', 'S3')

% plot(yscaledabs)
% xlim([0, w2+15])

% fs = 1/Ts;
% freq = (0:length(yscaledabs)-1)*fs/length(yscaledabs);
% fshift = (-samples/2 : samples/2-1)*(fs/samples);

% fig = figure;
% plot(freq, yscaledabs)
% xlim([0, freq(w2+15)])
% ylim([0, 1])
% xlabel('Frequency (Hz)')
% ylabel('Normalised Voltage (a.u.)')
% title('Normalised Voltage From ADC vs Frequency', "With Gasussian Noise of SNR = " + int2str(SNR) + " dB")
% annotation(fig,'textbox', [0.664285714285712 0.401357155913399 0.212499994199191 0.461904748848507],'String',...
%     ["S0_{real} = " + num2str(S0, '%5.4f'), ...
%     "S0_{calc} = " + num2str(S0_calc, '%5.4f'), ...
%     "S1_{real} = " + num2str(S1, '%5.4f'), ...
%     "S1_{calc} = " + num2str(S1_calc, '%5.4f'), ...
%     "S2_{real} = " + num2str(S2, '%5.4f'), ...
%     "S2_{calc} = " + num2str(S2_calc, '%5.4f'), ...
%     "S3_{real} = " + num2str(S3, '%5.4f'), ...
%     "S3_{calc} = " + num2str(S3_calc, '%5.4f')], 'FitBoxToText', 'on', 'BackgroundColor',[1 1 1]);
% grid on

% pause
% clf
% 
% fig = figure;
% plot(yscaled)
% xlabel('Real Normalised Voltage (a.u.)')
% ylabel('Imaginary Normalised Voltage (a.u.)')
% title('Complex FFT Results: Normalised Voltage From ADC', "With Gasussian Noise of SNR = " + int2str(SNR) + " dB")
% grid on
% 
% pause
% clf
% 
% hold on
% plot(theta * 180 / pi, IthetaNoise)
% plot(theta * 180 / pi, Itheta)
% xlim([0 360])
% xticks(0:45:360);
% xlabel('Motor Angle (°)')
% ylabel('Voltage (V)')
% title('Voltage From ADC vs Time', "With Gasussian Noise of SNR = " + int2str(SNR) + " dB")
% hold off

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