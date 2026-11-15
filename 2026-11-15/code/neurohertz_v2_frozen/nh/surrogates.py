"""Iterative amplitude-adjusted Fourier transform (IAAFT) surrogates.

A surrogate keeps a signal's power spectrum and amplitude distribution but destroys any
temporal structure beyond them (Schreiber & Schmitz 1996). Comparing a statistic on the
real signal with the same statistic on surrogates isolates the part of that statistic that
is NOT explained by the spectrum -- e.g. gamma frequency instability beyond what gamma
power, bandwidth and the 1/f background predict.
"""
from __future__ import annotations

import numpy as np


def iaaft(x: np.ndarray, rng: np.random.Generator, iterations: int = 50) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    n = x.size
    amp = np.abs(np.fft.rfft(x))
    sorted_x = np.sort(x)
    s = rng.permutation(x)
    for _ in range(iterations):
        S = np.fft.rfft(s)
        s = np.fft.irfft(amp * np.exp(1j * np.angle(S)), n=n)
        ranks = np.argsort(np.argsort(s))
        s = sorted_x[ranks]
    return s


def iaaft_chunked(x: np.ndarray, rng: np.random.Generator, iterations: int, chunk: int) -> np.ndarray:
    """IAAFT applied independently to consecutive chunks (respects slow non-stationarity)."""
    out = np.empty_like(x, dtype=float)
    n = x.size
    starts = list(range(0, n, chunk))
    for st in starts:
        stop = min(st + chunk, n)
        if stop - st < chunk // 4 and st > 0:      # merge a short tail into the previous chunk
            prev = starts[starts.index(st) - 1]
            out[prev:stop] = iaaft(x[prev:stop], rng, iterations)
        else:
            out[st:stop] = iaaft(x[st:stop], rng, iterations)
    return out
