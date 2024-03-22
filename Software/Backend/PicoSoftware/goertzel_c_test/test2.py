import time

from scipy.fft import fft
import matplotlib.pyplot as plt
import numpy as np

x = np.loadtxt("test_data2.csv")

x = x / 65535

cycles = 2*np.pi

# for cycle in [x / 10.0 for x in range(50, 70, 1)]:
# print(cycle)
N = len(x)

fs = N / cycles

num_freqs = 30

mags = [0] * num_freqs

for f in range(0,num_freqs):

    k0 = N * f / fs  # check the article on discrete frequency for this step

    omega_I = np.cos(k0 / N)
    omega_Q = np.sin(k0 / N)
    v1 = 0
    v2 = 0
    for n in range(N):
        v = 2 * omega_I * v1 - v2 + x[n]  # see the IIR Eq (3)
        v2 = v1
        v1 = v

    # Now value of v is in v1 and that of v1 is in v2
    y_I = v1 - omega_I * v2 # see the FIR Eq (2)
    y_Q = omega_Q * v2

    mags[f] = (y_I ** 2 + y_Q ** 2)   # figure below plotted after square root

mags[0] = mags[0] / 2

w = np.linspace(0, len(mags), len(mags))

w0 = 0
w1 = 1 + (2 * 5)
w2 = 1 + (4 * 5)

print(mags[w0], mags[w1], mags[w2])

# plot
fig, ax = plt.subplots()

ax.plot(w, mags, linewidth=1.0)

# ax.set(xlim=(0, 30), ylim=(0, 1))

ax.set(xlim=(0, num_freqs))

plt.show()
    # input()