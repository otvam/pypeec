import PyPEEC.config as config

# get config
FFT_SOLVER = config.FFT_SOLVER
FFT_THREAD = config.FFT_THREAD
FFT_CACHE_TIMEOUT = config.FFT_CACHE_TIMEOUT
FFT_BYTE_ALIGN = config.FFT_BYTE_ALIGN

# import the right library
if FFT_SOLVER == "NumPy":
    import numpy.fft as fftn
elif FFT_SOLVER == "SciPy":
    import scipy.fft as ffts
elif FFT_SOLVER == "FFTW":
    import pyfftw
    import pyfftw.interfaces.numpy_fft as fftw
    import pyfftw.interfaces.cache as cache

    cache.enable()
    cache.set_keepalive_time(FFT_CACHE_TIMEOUT)
else:
    raise ValueError("invalid FFT library")


def get_fftn(mat, shape):
    if FFT_SOLVER == "NumPy":
        mat_trf = fftn.fftn(mat, shape)
    elif FFT_SOLVER == "SciPy":
        mat_trf = ffts.fftn(mat, shape)
    elif FFT_SOLVER == "FFTW":
        mat = pyfftw.byte_align(mat, n=FFT_BYTE_ALIGN)
        mat_trf = fftw.fftn(mat, shape, threads=FFT_THREAD)
    else:
        raise ValueError("invalid FFT library")

    return mat_trf


def get_ifftn(mat, shape):
    if FFT_SOLVER == "NumPy":
        mat_trf = fftn.ifftn(mat, shape)
    elif FFT_SOLVER == "SciPy":
        mat_trf = ffts.ifftn(mat, shape)
    elif FFT_SOLVER == "FFTW":
        print("sfsdf")
        mat = pyfftw.byte_align(mat, n=FFT_BYTE_ALIGN)
        mat_trf = fftw.ifftn(mat, shape, threads=FFT_THREAD)
    else:
        raise ValueError("invalid FFT library")

    return mat_trf
