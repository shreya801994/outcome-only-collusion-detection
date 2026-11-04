"""Option B: a competitive-consistency test that allows partial price adjustment.

Null model (the simulator's competitive rule, docs/SIMULATION_POLICIES.md):
    p_i,t = p_i,t-1 + lambda_i * (BR_i(p_j,t-1; a_t, c_i) - p_i,t-1) + e_i,t
with unknown cost c_i and unknown adjustment speed lambda_i.

What the auditor uses (level L3: prices, quantities, market size; mu known):
  * observed inside shares s_i,t = q_i,t / Q_t and outside share s_0,t;
  * the logit inversion a_hat_i,t = p_i,t + mu * log(s_i,t / s_0,t)  (a_0 = 0 is a normalisation),
    which recovers the current demand state exactly (Proposition 1, docs/PROPOSITION_v3.md);
  * hence the competitive target BR_i,t(c) = BR(p_j,t-1; a_hat_t, c) for any candidate cost c.
No cost, attractiveness path, agent parameter or label is used.

Procedure, per firm i, on the scoring window:
  1. Cost and speed.  For each c on a grid, fit the restricted model
         dp_t = lambda * (BR_t(c) - p_t-1) + e_t
     by Huber regression through the origin; c_hat minimises the robust residual scale (MAD),
     refined by golden-section search.  lambda_hat is the estimated adjustment speed.
  2. Test.  At c_hat, fit the unrestricted model
         dp_t = alpha + beta * p_t-1 + gamma * BR_t(c_hat) + e_t
     by Huber regression with a heteroskedasticity-robust sandwich covariance.  Competitive
     partial adjustment implies gamma + beta = 0 (full response to the target, any lambda).  A
     price rule that ignores the competitive target (e.g. a fixed cartel price) gives gamma ~ 0,
     beta = -lambda, so gamma + beta < 0.
  3. Statistic t_i = (gamma + beta) / se.
Score = max over firms of -t_i (higher = less consistent with competitive partial adjustment).
Under the null t_i is approximately N(0, 1) whatever lambda_i is, which is the point of Option B.

Optional: mu estimated jointly (common to both firms) by profiling over a grid.
"""
import numpy as np
from scipy.special import lambertw

HUBER_K = 1.345
C_GRID = np.round(np.arange(-0.5, 2.5001, 0.02), 4)


def recovered_attractiveness(price, share, mu, a0=0.0):
    """a_hat_i,t from observed prices and inside shares (logit inversion)."""
    s0 = 1.0 - share.sum(axis=-1, keepdims=True)
    return price + mu * np.log(share / s0) + a0


def br_target(c, a_i, a_j, p_j_lag, mu, a0=0.0):
    """Static best response to the rival's previous price under the current demand state."""
    log_a = np.logaddexp(a0 / mu, (a_j - p_j_lag) / mu)
    z = np.exp((a_i - c) / mu - 1.0 - log_a)
    return c + mu * (1.0 + np.real(lambertw(z)))


def _mad(r, axis=-1):
    med = np.median(r, axis=axis, keepdims=True)
    return 1.4826 * np.median(np.abs(r - med), axis=axis)


def _huber_origin(y, x, iters=20):
    """Huber regression of y on x through the origin, vectorised over leading axes."""
    lam = (x * y).sum(-1) / np.maximum((x * x).sum(-1), 1e-300)
    for _ in range(iters):
        r = y - lam[..., None] * x
        s = np.maximum(_mad(r), 1e-12)
        u = np.abs(r) / (HUBER_K * s[..., None])
        w = np.where(u <= 1, 1.0, 1.0 / np.maximum(u, 1e-300))
        lam = (w * x * y).sum(-1) / np.maximum((w * x * x).sum(-1), 1e-300)
    r = y - lam[..., None] * x
    return lam, _mad(r)


def _huber_ols(y, X, iters=50):
    """Huber regression with sandwich covariance. y (n,), X (n, k)."""
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    for _ in range(iters):
        r = y - X @ beta
        s = max(_mad(r), 1e-12)
        u = np.abs(r) / (HUBER_K * s)
        w = np.where(u <= 1, 1.0, 1.0 / u)
        Xw = X * w[:, None]
        new = np.linalg.solve(X.T @ Xw, Xw.T @ y)
        if np.max(np.abs(new - beta)) < 1e-12:
            beta = new
            break
        beta = new
    r = y - X @ beta
    s = max(_mad(r), 1e-12)
    u = r / (HUBER_K * s)
    psi = np.clip(u, -1, 1) * HUBER_K * s          # Huber psi(r)
    dpsi = (np.abs(u) <= 1).astype(float)          # psi'(r)
    bread = np.linalg.pinv(X.T @ (X * dpsi[:, None]))
    meat = X.T @ (X * (psi ** 2)[:, None])
    cov = bread @ meat @ bread
    return beta, cov


def _golden(f, lo, hi, iters=30):
    g = (np.sqrt(5) - 1) / 2
    a, b = lo, hi
    x1, x2 = b - g * (b - a), a + g * (b - a)
    f1, f2 = f(x1), f(x2)
    for _ in range(iters):
        if f1 < f2:
            b, x2, f2 = x2, x1, f1
            x1 = b - g * (b - a)
            f1 = f(x1)
        else:
            a, x1, f1 = x1, x2, f2
            x2 = a + g * (b - a)
            f2 = f(x2)
    return (a + b) / 2


def firm_design(price, a_hat, i, start):
    """Arrays for firm i over periods start..T-1 (needs t-1 >= 0)."""
    j = 1 - i
    t = np.arange(max(start, 1), price.shape[0])
    return dict(dp=price[t, i] - price[t - 1, i], p_lag=price[t - 1, i], pj_lag=price[t - 1, j],
                a_i=a_hat[t, i], a_j=a_hat[t, j])


def fit_firm(d, mu, c_grid=C_GRID):
    """Estimate (c, lambda) for one firm and return the test statistic."""
    tgt = br_target(c_grid[:, None], d["a_i"][None], d["a_j"][None], d["pj_lag"][None], mu)
    x = tgt - d["p_lag"][None]
    lam_g, scale_g = _huber_origin(np.broadcast_to(d["dp"], x.shape), x)
    k = int(np.argmin(scale_g))
    lo, hi = c_grid[max(k - 1, 0)], c_grid[min(k + 1, len(c_grid) - 1)]

    def crit(c):
        xx = br_target(c, d["a_i"], d["a_j"], d["pj_lag"], mu) - d["p_lag"]
        return float(_huber_origin(d["dp"][None], xx[None])[1][0])

    c_hat = _golden(crit, lo, hi) if hi > lo else float(c_grid[k])
    xx = br_target(c_hat, d["a_i"], d["a_j"], d["pj_lag"], mu) - d["p_lag"]
    lam_hat, scale = _huber_origin(d["dp"][None], xx[None])
    br = br_target(c_hat, d["a_i"], d["a_j"], d["pj_lag"], mu)
    X = np.column_stack([np.ones_like(br), d["p_lag"], br])
    b, cov = _huber_ols(d["dp"], X)
    r = np.array([0.0, 1.0, 1.0])
    se = float(np.sqrt(max(r @ cov @ r, 1e-300)))
    t = float((b[1] + b[2]) / se)
    resid = d["dp"] - lam_hat[0] * xx
    return {"c_hat": float(c_hat), "lambda_hat": float(lam_hat[0]), "scale": float(scale[0]),
            "gamma": float(b[2]), "beta": float(b[1]), "t": t, "profile_loss": float(scale[0]),
            **residual_dependence(resid)}


def residual_dependence(resid, lags=5):
    """Serial dependence of restricted-model residuals (white noise under the null, for any lambda).

    Residuals are winsorised at 3 robust SDs so that exogenous price cuts do not dominate.
    Returns sqrt(n) * rho_1 (approx. N(0,1) under the null) and the Box-Pierce statistic over `lags`.
    """
    r = resid - np.median(resid)
    s = max(_mad(r), 1e-12)
    r = np.clip(r, -3 * s, 3 * s)
    r = r - r.mean()
    n = len(r)
    den = float(r @ r)
    rho = np.array([float(r[k:] @ r[:-k]) / den for k in range(1, lags + 1)])
    return {"z_ac1": float(np.sqrt(n) * rho[0]), "box_pierce": float(n * (rho ** 2).sum())}


def score_run(price, quantity, market_size, mu=0.25, start=50, estimate_mu=False,
              mu_grid=np.round(np.arange(0.15, 0.3501, 0.01), 4)):
    """Option B score for one run (price, quantity: (T, 2); market_size: (T,))."""
    price = np.asarray(price, float)
    share = np.clip(np.asarray(quantity, float) / np.asarray(market_size, float)[:, None], 1e-9, 1 - 1e-9)
    mus = mu_grid if estimate_mu else [mu]
    best = None
    for m in mus:
        a_hat = recovered_attractiveness(price, share, m)
        fits = [fit_firm(firm_design(price, a_hat, i, start), m) for i in (0, 1)]
        loss = sum(np.log(f["profile_loss"]) for f in fits)
        if best is None or loss < best[0]:
            best = (loss, m, fits)
    _, m, fits = best
    return {"score": max(-f["t"] for f in fits), "mu_hat": float(m),
            "score_ac1": max(f["z_ac1"] for f in fits), "score_bp": max(f["box_pierce"] for f in fits),
            "t_1": fits[0]["t"], "t_2": fits[1]["t"],
            "c_hat_1": fits[0]["c_hat"], "c_hat_2": fits[1]["c_hat"],
            "lambda_hat_1": fits[0]["lambda_hat"], "lambda_hat_2": fits[1]["lambda_hat"]}
