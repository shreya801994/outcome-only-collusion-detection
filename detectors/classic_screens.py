"""Published cartel screens for price time series, as benchmarks (addendum 5).

All take prices only (auditor level L1) on the scoring window; higher score = more suspicious.

V1  Variance screen (Abrantes-Metz, Froeb, Geweke & Taylor 2006, International Journal of
    Industrial Organization 24(3): 467-486): coefficient of variation SD(p)/mean(p) per firm;
    low variation is the collusion marker.  Score = -mean over firms of CV.
V2  Price-change variance: SD of first differences per firm; lower price-change variance under
    collusion is the hypothesis of Bolotova, Connor & Miller (2008, IJIO 26(6): 1290-1307), whose
    own test needs a known cartel period and so cannot be used as a screen.  Score = -mean SD.
V3  Distribution of price changes (Blanckenburg, Geist & Kholodilin 2012, German Economic Review
    13(3): 245-256, who use a Kolmogorov-Smirnov comparison of collusive and non-collusive price
    changes).  Adapted here to screening: KS distance between each firm's price-change
    distribution and a reference distribution of competitive price changes taken from the
    calibration split.  Score = max over firms of the KS statistic.
"""
import numpy as np
from scipy.stats import ks_2samp


def cv_screen(price):
    p = np.asarray(price, float)
    return float(-np.mean(p.std(axis=0, ddof=1) / p.mean(axis=0)))


def sd_change_screen(price):
    dp = np.diff(np.asarray(price, float), axis=0)
    return float(-np.mean(dp.std(axis=0, ddof=1)))


def reference_changes(price_runs):
    """Pooled competitive price changes from calibration runs, shape (runs, T, 2)."""
    return np.diff(np.asarray(price_runs, float), axis=1).ravel()


def ks_screen(price, reference):
    dp = np.diff(np.asarray(price, float), axis=0)
    return float(max(ks_2samp(dp[:, i], reference).statistic for i in range(dp.shape[1])))
