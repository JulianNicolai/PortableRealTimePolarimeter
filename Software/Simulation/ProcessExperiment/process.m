data = readmatrix('LPF02.csv');
data(:, 1) = (data(:, 1) - data(1, 1)) * 1000;
err = 3.0289277684;
% err = 1;
% data(:, 2) = data(:, 2) / (err^2);
% avg = mean(data(:, 2));
% data(:, 2) = data(:, 2) + avg * (1 - 1/(err^2));

for i = 1:1

    START_POINT = 2743;  % 1/2 cycle: 2743 to 9698
    END_POINT = 127890 + i;

    time_data = data(START_POINT:END_POINT, 1);
    volt_data = data(START_POINT:END_POINT, 2);

    % plot(time_data, volt_data);

    samples = length(volt_data);

    y = fft(volt_data);
    ymod = y(1:floor(samples / 2)) / samples;
    yscaled = [ymod(1); ymod(2:end) * 2];

    cycles = 9;

    w1 = 1 + (2 * cycles);
    w2 = 1 + (4 * cycles);

    A0 = yscaled(1);
    A1 = yscaled(round(w1));
    A2 = yscaled(round(w2));

    S1c = real(A2) * 4;
    S2c = imag(A2) * -4;
    S3c = imag(A1) * -2;
    S0c = 2*A0 - S1c/2;
    
    Ex = sqrt((S0c + S1c)/2);
    Ey = sqrt((S0c - S1c)/2);
    DOP = sqrt(S1c^2 + S2c^2 + S3c^2) / S0c
    E = sqrt(Ex^2 + Ey^2)

%     plot(abs(yscaled))
%     plot(angle(yscaled))
%     xlim([0 70])
%     ylim([-pi pi])
%     xline(w1)
%     xline(w2)
    
%     disp([i S0_calc S1_calc S2_calc S3_calc])
    
%     pause
    
end