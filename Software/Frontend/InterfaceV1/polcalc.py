import math
import numpy as np
from numpy import sin, cos
from scipy.fft import fft


class PolarisationStateTracker:

    def __init__(self):
        ellipse_resolution = 256
        self.t = np.linspace(0, 2 * np.pi, ellipse_resolution)
        self.S0 = 0.0
        self.S1 = 0.0
        self.S2 = 0.0
        self.S3 = 0.0

    def calculate_stokes_from_measurements(self, intensity_data, num_of_cycles, num_of_samples):

        y = fft(intensity_data)

        # All parameters must be scaled by the number of samples taken
        # Parameters required: DC (index: 0), 2ω (index: 2*cycles), 4ω (index: 4*cycles)
        # Due to FFT symmetry, total intensity at a frequency is actually x2, except for DC (0 Hz, already symmetric)
        A0 = y[0] / num_of_samples
        A1 = y[num_of_cycles * 2] * (2 / num_of_samples)
        A2 = y[num_of_cycles * 4] * (2 / num_of_samples)

        self.S1 = np.real(A2) * 4
        self.S2 = np.imag(A2) * -4
        self.S3 = np.imag(A1) * -2
        self.S0 = 2 * np.real(A0) - self.S1 / 2

    def generate_random_polarisation(self):
        Ex = np.random.random()
        Ey = np.sqrt(1 - Ex**2)
        phi = np.random.random() * 2 * np.pi
        Ey = Ey * np.exp(1j * phi)

        self.S0 = np.real(Ex * np.conj(Ex) + Ey * np.conj(Ey))
        self.S1 = np.real(Ex * np.conj(Ex) - Ey * np.conj(Ey))
        self.S2 = np.real(Ex * np.conj(Ey) + Ey * np.conj(Ex))
        self.S3 = np.real(1j * (Ex * np.conj(Ey) - Ey * np.conj(Ex)))

        print("New random state generated.")

    def get_stokes_params(self):
        return [self.S0, self.S1, self.S2, self.S3]

    def get_dop(self):
        return np.sqrt(self.S1 ** 2 + self.S2 ** 2 + self.S3 ** 2) / self.S0

    def get_polarisation_ellipse_params(self):
        K = 0 if self.S1 >= 0 else np.pi / 2
        psi = math.atan(self.S2 / self.S1) / 2 - K
        chi = math.asin(self.S3 / self.S0) / 2
        return psi, chi

    def get_poincare_sphere_params(self):
        phi, theta = self.get_polarisation_ellipse_params()
        phi *= 2
        theta *= 2
        return phi, theta

    def get_polarisation_ellipse_xy_data(self):

        psi, chi = self.get_polarisation_ellipse_params()

        sin_t = sin(self.t)
        cos_t = cos(self.t)

        x_t = np.sqrt(self.S0) * (cos(chi) * cos(psi) * sin_t - sin(chi) * sin(psi) * cos_t)
        y_t = np.sqrt(self.S0) * (cos(chi) * sin(psi) * sin_t + sin(chi) * cos(psi) * cos_t)

        return x_t, y_t
