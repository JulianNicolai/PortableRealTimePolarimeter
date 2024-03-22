from scipy.fft import fft
import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt("test_data2.csv")

data = data

# make data
y = abs(fft(data)) * 2 / (len(data) * 65535)
y[0] = y[0] / 2
x = np.linspace(0, len(y), len(y))

# plot
fig, ax = plt.subplots()

ax.plot(x, y, linewidth=1.0)

# ax.set(xlim=(0, 30), ylim=(0, 1))

ax.set(xlim=(0, 30))

plt.show()