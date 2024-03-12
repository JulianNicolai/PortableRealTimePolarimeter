% Polarization Simulation
close all
% clear all
RPM = 3840;  % [RPM] max
cycles_per_sec = RPM / 60;  % [Hz]
samples_per_sec = 166e3;  % Samples per second
cycles = 5; % Number of cycles

samples_per_cycle = samples_per_sec / cycles_per_sec;  % Samples per cycle

integ_time = cycles / cycles_per_sec;  % [s]
fps = 1/integ_time;

SNR = 10;

Ts = 2*pi/samples_per_cycle;

theta = 0 : Ts : 2*pi*cycles - Ts;

NUMBER_OF_TESTS = 100;

errors = zeros(NUMBER_OF_TESTS, 8);

for i = 1:NUMBER_OF_TESTS

    % Choose Ex and Ey Values at Random
    Ex = rand(1);
    Ey = sqrt(1 - Ex^2);
    phi = rand(1) * 2*pi;
    Ey = Ey * exp(1i*phi);

    S0 = Ex * conj(Ex) + Ey * conj(Ey);
    S1 = Ex * conj(Ex) - Ey * conj(Ey);
    S2 = Ex * conj(Ey) + Ey * conj(Ex);
    S3 = 1i * (Ex * conj(Ey) - Ey * conj(Ex));

    Itheta = S0/2 + S1/4 + S3/2 * sin(2*theta) + S1/4 * cos(4*theta) + S2/4 * sin(4*theta);
    IthetaNoise = awgn(Itheta, SNR);

    % data = Itheta;
    data = IthetaNoise;

    % data_err = data(1:end - 2000);

    samples = length(data);
    cycles = samples / samples_per_sec * cycles_per_sec;
    
    CORRECTION_FACTOR = 2.0;
    w = hann(length(data)).' * CORRECTION_FACTOR;
    data_op = data(1:end) .* w;

    
    
    w1 = 1 + (2 * cycles);
    w2 = 1 + (4 * cycles);

    A0 = goertzel(data_op, 1) / samples;
    A1 = goertzel(data_op, w1) * 2 / samples;
    A2 = goertzel(data_op, w2) * 2 / samples;

    S1_calc_g = real(A2) * 4;
    S2_calc_g = imag(A2) * -4;
    S3_calc_g = imag(A1) * -2;
    S0_calc_g = 2*A0 - S1_calc_g/2;
 
    

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
    
    S0_g_err = (S0 - S0_calc_g);
    S1_g_err = (S1 - S1_calc_g);
    S2_g_err = (S2 - S2_calc_g);
    S3_g_err = (S3 - S3_calc_g);
    
    S0_f_err = (S0 - S0_calc);
    S1_f_err = (S1 - S1_calc);
    S2_f_err = (S2 - S2_calc);
    S3_f_err = (S3 - S3_calc);
    
    errors(i, :) = [S0_g_err S1_g_err S2_g_err S3_g_err S0_f_err S1_f_err S2_f_err S3_f_err];

end

hold on
plot(1:NUMBER_OF_TESTS, errors(:, 1) - errors(:, 5))
plot(1:NUMBER_OF_TESTS, errors(:, 2) - errors(:, 6))
plot(1:NUMBER_OF_TESTS, errors(:, 3) - errors(:, 7))
plot(1:NUMBER_OF_TESTS, errors(:, 4) - errors(:, 8))
hold off

legend(["S0", "S1", "S2", "S3"])
