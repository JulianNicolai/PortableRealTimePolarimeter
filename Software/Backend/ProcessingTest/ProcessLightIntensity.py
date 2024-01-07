import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft

# Load data from disk, this will be replaced with directly measured data
with open('data0.csv') as file:
    csvreader = csv.reader(file)

    theta = []
    I_theta = []
    for row in csvreader:
        theta.append(float(row[0]))
        I_theta.append(float(row[1]))

theta = np.array(theta)
I_theta = np.array(I_theta)

# print(theta)
# print(I_theta)

# The number of cycles/scan will be determined by user
cycles = 64
samples = len(theta)

y = fft(I_theta)

# All parameters must be scaled by the number of samples taken
# Parameters required: DC (index: 0), 2ω (index: 2*cycles), 4ω (index: 4*cycles)
A0 = y[0] / samples
A1 = y[cycles * 2] * (2 / samples)
A2 = y[cycles * 4] * (2 / samples)

S1_calc = np.real(A2) * 4
S2_calc = np.imag(A2) * -4
S3_calc = np.imag(A1) * -2
S0_calc = 2 * np.real(A0) - S1_calc / 2

print(S0_calc, S1_calc, S2_calc, S3_calc)

# fig, ax = plt.subplots()

# ax.plot(y_sub_abs, linewidth=2.0)

# ax.set(xlim=(0, 2*np.pi),
#        ylim=(0, 1))

# plt.show()
