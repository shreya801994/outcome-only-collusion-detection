"""Run-level evaluation metrics for the v2 experiments.

The unit of analysis is always a complete run.
"""

import numpy as np
from scipy.stats import norm, rankdata


def auc(pos, neg):
    """Probability that a positive scores higher than a negative (ties count 1/2)."""
    pos = np.asarray(pos, dtype=float)
    neg = np.asarray(neg, dtype=float)
    ranks = rankdata(np.concatenate([pos, neg]))
    n1, n2 = len(pos), len(neg)
    return (ranks[:n1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n2)


def _auc_rows(pos, neg):
    """Row-wise AUC for 2-D arrays (bootstrap replicates in rows)."""
    n1, n2 = pos.shape[1], neg.shape[1]
    ranks = rankdata(np.concatenate([pos, neg], axis=1), axis=1)
    return (ranks[:, :n1].sum(axis=1) - n1 * (n1 + 1) / 2.0) / (n1 * n2)


def bootstrap_auc(pos, neg, strata_pos=None, strata_neg=None, n_boot=2000, seed=0, within=False):
    """AUC point estimate and percentile 95% CI.

    within=False: pooled AUC; resampling is stratified by class (and by stratum if given).
    within=True : mean of per-stratum AUCs; resampling within each stratum and class.
    """
    rng = np.random.default_rng(seed)
    pos = np.asarray(pos, dtype=float)
    neg = np.asarray(neg, dtype=float)
    if strata_pos is None:
        strata_pos = np.zeros(len(pos), dtype=int)
        strata_neg = np.zeros(len(neg), dtype=int)
    strata = sorted(set(strata_pos) & set(strata_neg))

    if within:
        estimates = []
        boots = []
        for s in strata:
            ps, ns = pos[strata_pos == s], neg[strata_neg == s]
            estimates.append(auc(ps, ns))
            bp = ps[rng.integers(0, len(ps), size=(n_boot, len(ps)))]
            bn = ns[rng.integers(0, len(ns), size=(n_boot, len(ns)))]
            boots.append(_auc_rows(bp, bn))
        est = float(np.mean(estimates))
        boot = np.mean(np.vstack(boots), axis=0)
    else:
        est = float(auc(pos, neg))
        bp_parts, bn_parts = [], []
        for s in strata:
            ps, ns = pos[strata_pos == s], neg[strata_neg == s]
            bp_parts.append(ps[rng.integers(0, len(ps), size=(n_boot, len(ps)))])
            bn_parts.append(ns[rng.integers(0, len(ns), size=(n_boot, len(ns)))])
        boot = _auc_rows(np.hstack(bp_parts), np.hstack(bn_parts))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return est, float(lo), float(hi)


def wilson(successes, total, conf=0.95):
    if total == 0:
        return float("nan"), float("nan")
    z = norm.ppf(1 - (1 - conf) / 2)
    p = successes / total
    den = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / den
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def threshold_95(calibration_scores):
    """Frozen threshold: 95th percentile of calibration scores (flag if score > threshold)."""
    return float(np.quantile(np.asarray(calibration_scores, dtype=float), 0.95))
