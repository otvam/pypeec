"""
Module for handling Fourier series (through FFT/IFFT).

This module is a simple wrapper for FFT/IFFT functions:
    - the time-domain signals are real and periodic
    - use exclusively the positive-frequency terms
    - scale the output as peak value Fourier coefficients
    - scale the DC coefficient correspondingly
    - handle undersampling/oversampling for the IFFT
    - handle truncation/padding for the FFT
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.fft as fft


def get_fft(v_time, n_freq=None):
    """
    Get the Fourier series of a real periodic signal.
    The number of frequencies can be specified (truncation/padding).
    """

    # compute the FFT
    v_freq = fft.rfft(v_time)

    # peak value spectrum scaling
    v_freq = 2 * v_freq / len(v_time)

    # scale the DC coefficient
    v_freq[0] *= 0.5

    # if the required size is specified, use truncation/padding
    if n_freq is not None:
        # pad the frequencies with zeros
        v_pad = np.zeros(np.maximum(0, n_freq - len(v_freq)))
        v_freq = np.concatenate((v_freq, v_pad))

        # truncate the frequencies to the length
        v_freq = v_freq[:n_freq]

    return v_freq


def get_ifft(v_freq, n_time=None):
    """
    Get the real periodic signal of a Fourier series.
    The number of samples can be specified (undersampling/oversampling).
    """

    # scale the DC coefficient
    v_freq[0] *= 2.0

    # if the required size is specified, use undersampling/oversampling
    if n_time is not None:
        v_time = fft.irfft(v_freq, n_time)
    else:
        v_time = fft.irfft(v_freq)

    # peak value spectrum scaling
    v_time = 0.5 * v_time * len(v_time)

    return v_time


def get_time(f, n_time):
    """
    Get a time vector.
    """

    t_vec = np.arange(n_time) / (f * n_time)

    return t_vec


def get_freq(f, n_freq):
    """
    Get a frequency vector.
    """

    f_vec = np.arange(n_freq) * f

    return f_vec
