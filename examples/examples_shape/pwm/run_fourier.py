"""
Compute non-sinusoidal waveforms with Fourier analysis:
    - extract the frequency domain impedance
    - compute the waveforms in the frequency domain
    - transform back the results in the time domain
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

# base packages
import os
import scilogger
import scisave
import pypeec

# import numerical library
import numpy as np

# import plotting library
import matplotlib.pyplot as plt

# import utils to be demonstrated
from pypeec.utils import fourier

# get a logger
LOGGER = scilogger.get_logger(__name__, "script")

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)


def _solve_peec(folder_example, folder_config):
    """
    Solve the PEEC problem (mesher and solver).
    """

    # define the input
    file_geometry = os.path.join(folder_example, "geometry.yaml")
    file_problem = os.path.join(folder_example, "problem.yaml")

    # define the configuration
    file_tolerance = os.path.join(folder_config, "tolerance.yaml")

    # define the output
    file_voxel = os.path.join(folder_example, "voxel.pkl")
    file_solution = os.path.join(folder_example, "solution.pkl")

    # run the workflow and load the solution
    pypeec.run_mesher_file(
        file_geometry=file_geometry,
        file_voxel=file_voxel,
    )
    pypeec.run_solver_file(
        file_voxel=file_voxel,
        file_problem=file_problem,
        file_tolerance=file_tolerance,
        file_solution=file_solution,
    )
    data_solution = scisave.load_data(file_solution)

    return data_solution


def _get_impedance_peec(data_solution):
    """
    Extract the resistance and inductance values (from the solution).
    """

    # extract the data
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    # check solution
    assert isinstance(data_init, dict), "invalid solution"
    assert isinstance(data_sweep, dict), "invalid solution"

    # init the impedance vector
    f_sim = np.zeros(len(data_sweep), dtype=np.float64)
    Z_sim = np.zeros(len(data_sweep), dtype=np.complex128)

    # find the impedance for the different frequencies
    for idx, data_sweep_tmp in enumerate(data_sweep.values()):
        # extract the data
        freq = data_sweep_tmp["freq"]
        source = data_sweep_tmp["source"]

        # extract the impedance
        voltage = source["src"]["V"] - source["sink"]["V"]
        current = (source["src"]["I"] - source["sink"]["I"]) / 2
        impedance = voltage / current

        # assign
        f_sim[idx] = freq
        Z_sim[idx] = impedance

    # extract the equivalent circuit
    R_sim = np.real(Z_sim)
    L_sim = np.imag(Z_sim) / (2 * np.pi * f_sim)

    return f_sim, R_sim, L_sim


def _get_impedance_fourier(f_vec, f_sim, R_sim, L_sim):
    """
    Interpolate the impedance at the Fourier frequencies.
    """

    # clip to prevent extrapolation
    f_clamp_vec = np.clip(f_vec, np.min(f_sim), np.max(f_sim))

    # interpolate the circuit parameters (log-scale frequency)
    R_freq = np.interp(np.log10(f_clamp_vec), np.log10(f_sim), R_sim)
    L_freq = np.interp(np.log10(f_clamp_vec), np.log10(f_sim), L_sim)

    # assemble the impedance
    Z_freq = R_freq + (1j * 2 * np.pi * f_vec) * L_freq

    return Z_freq


def _plot_circuit(f_sim, R_sim, L_sim):
    """
    Plot the extracted resistance and inductance values.
    """

    (fig, ax) = plt.subplots(2, 1)

    ax[0].semilogx(f_sim, 1e3 * R_sim, "o-")
    ax[0].set_xlabel("f (Hz)")
    ax[0].set_ylabel("R (mOhm)")
    ax[0].set_title("Resistance")
    ax[0].grid()

    ax[1].semilogx(f_sim, 1e9 * L_sim, "o-")
    ax[1].set_xlabel("f (Hz)")
    ax[1].set_ylabel("L (nH)")
    ax[1].set_title("Inductance")
    ax[1].grid()

    fig.tight_layout()


def _plot_frequency(f_vec, V_freq, I_freq, n_plot):
    """
    Plot the voltage and current spectrums.
    """

    f_vec = f_vec[:n_plot]
    V_freq = V_freq[:n_plot]
    I_freq = I_freq[:n_plot]

    (fig, ax) = plt.subplots(2, 1)

    ax[0].plot(1e-3 * f_vec, np.abs(V_freq), "o-")
    ax[0].set_xlabel("f (kHz)")
    ax[0].set_ylabel("V (V)")
    ax[0].set_title("Voltage - Frequency Domain")
    ax[0].grid()

    ax[1].plot(1e-3 * f_vec, np.abs(I_freq), "o-")
    ax[1].set_xlabel("f (kHz)")
    ax[1].set_ylabel("I (A)")
    ax[1].set_title("Current - Frequency Domain")
    ax[1].grid()

    fig.tight_layout()


def _plot_power(f_vec, P_vec, Q_vec, n_plot):
    """
    Plot the power (active and reactive) spectrums.
    """

    f_vec = f_vec[:n_plot]
    P_vec = P_vec[:n_plot]
    Q_vec = Q_vec[:n_plot]

    (fig, ax) = plt.subplots(2, 1)

    ax[0].plot(1e-3 * f_vec, np.abs(P_vec), "o-")
    ax[0].set_xlabel("f (kHz)")
    ax[0].set_ylabel("P (W)")
    ax[0].set_title("Active Power - Frequency Domain")
    ax[0].grid()

    ax[1].plot(1e-3 * f_vec, np.abs(Q_vec), "o-")
    ax[1].set_xlabel("f (kHz)")
    ax[1].set_ylabel("Q (VA)")
    ax[1].set_title("Reative Power - Frequency Domain")
    ax[1].grid()

    fig.tight_layout()


def _plot_waveform(t_vec, V_time, I_time):
    """
    Plot the voltage and current waveforms.
    """

    (fig, ax) = plt.subplots(2, 1)

    ax[0].plot(1e6 * t_vec, V_time, "-")
    ax[0].set_xlabel("t (us)")
    ax[0].set_ylabel("V (V)")
    ax[0].set_title("Voltage - Time Domain")
    ax[0].grid()

    ax[1].plot(1e6 * t_vec, I_time, "-")
    ax[1].set_xlabel("t (us)")
    ax[1].set_ylabel("I (A)")
    ax[1].set_title("Current - Time Domain")
    ax[1].grid()

    fig.tight_layout()


if __name__ == "__main__":
    # ########################################################
    # ### solve the PEEC problem
    # ########################################################

    # folder containing the example files
    folder_example = os.path.join(PATH_ROOT, ".")

    # folder containing the global configuration files
    folder_config = os.path.join(PATH_ROOT, "..", "..", "config")

    # solve the PEEC problem
    data_solution = _solve_peec(folder_example, folder_config)

    # ########################################################
    # ### define the time domain voltage excitation
    # ########################################################

    LOGGER.info("define the time domain voltage excitation")

    # parameters for the signal
    d_pulse = 0.10  # duty cycle of the PWM pulses
    d_wait = 0.20  # duty cycle between the PWM pulses
    V_pwm = 1.0  # peak value for the PWM voltage
    f_pwm = 50e3  # fundamental frequency of the signal
    f_cut = 5.0e6  # cutoff frequency for the low-pass filter
    n_time = 2000  # number of time domain samples
    n_freq = 1000  # number of frequencies for the FFT
    n_plot = 21  # number of frequencies to be plotted

    # get the time and frequency vectors
    t_vec = fourier.get_time(f_pwm, n_time)
    f_vec = fourier.get_freq(f_pwm, n_freq)

    # indices of the positive and negative PWM pulses
    idx_pos = (t_vec > (0.5 - d_wait / 2 - d_pulse / 2) / f_pwm) & (t_vec < (0.5 - d_wait / 2 + d_pulse / 2) / f_pwm)
    idx_neg = (t_vec > (0.5 + d_wait / 2 - d_pulse / 2) / f_pwm) & (t_vec < (0.5 + d_wait / 2 + d_pulse / 2) / f_pwm)

    # construct the time domain excitation
    V_time = np.zeros(n_time, dtype=np.float64)
    V_time[idx_pos] = +V_pwm
    V_time[idx_neg] = -V_pwm

    # ########################################################
    # ### compute the waveforms in the frequency domain
    # ########################################################

    LOGGER.info("compute the waveforms with Fourier analysis")

    # extract the resistance and inductance values
    (f_sim, R_sim, L_sim) = _get_impedance_peec(data_solution)

    # transform the voltage into the frequency domain
    V_freq = fourier.get_fft(V_time, n_freq=n_freq)

    # apply the low-pass filter to the voltage
    V_freq = (V_freq * f_cut) / (f_cut + 1j * f_vec)

    # interpolate the impedance at the Fourier frequencies
    Z_freq = _get_impedance_fourier(f_vec, f_sim, R_sim, L_sim)

    # compute the inductor current with the impedance
    I_freq = V_freq / Z_freq

    # ########################################################
    # ### compute the complex power harmonics
    # ########################################################

    LOGGER.info("compute the complex power harmonics")

    # compute the complex power spectrum
    S_vec = 0.5 * V_freq * np.conj(I_freq)

    # get the correct scaling for the DC power
    S_vec[0] *= 2.0

    # extract the active and reactive power spectrums
    P_vec = np.real(S_vec)
    Q_vec = np.imag(S_vec)

    # ########################################################
    # ### transform the waveforms in the time domain
    # ########################################################

    LOGGER.info("transform the waveforms in the time domain")

    # transform the waveforms back into the time domain
    V_time = fourier.get_ifft(V_freq, n_time=n_time)
    I_time = fourier.get_ifft(I_freq, n_time=n_time)

    # ########################################################
    # ### plot the waveforms and spectrums
    # ########################################################

    LOGGER.info("plot the waveforms and spectrums")

    # plot the extracted resistance and inductance values
    _plot_circuit(f_sim, R_sim, L_sim)

    # plot the voltage and current spectrums
    _plot_frequency(f_vec, V_freq, I_freq, n_plot)

    # plot the power (active and reactive) spectrums
    _plot_power(f_vec, P_vec, Q_vec, n_plot)

    # plot the voltage and current waveforms
    _plot_waveform(t_vec, V_time, I_time)

    # show the plots
    plt.show()
