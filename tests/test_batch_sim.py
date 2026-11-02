import numpy as np

from simulator.batch_sim import AgentParams, auditor_view, simulate_batch
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks
from simulator.equilibrium import nash


def _run(conduct, env, n=6, periods=120, seed=7, params=AgentParams()):
    ss = np.random.SeedSequence(seed)
    s_shock, s_par, s_noise, s_tr = ss.spawn(4)
    a, q = simulate_shocks(np.random.default_rng(s_shock), n, periods, ENVIRONMENTS[env])
    costs = np.column_stack([np.full(n, 0.9), np.full(n, 1.2)])
    return simulate_batch(costs, a, q, conduct, params,
                          np.random.default_rng(s_par), np.random.default_rng(s_noise),
                          np.random.default_rng(s_tr))


def test_reproducible_with_same_seed():
    r1 = _run("collusive_tracking", "E3")
    r2 = _run("collusive_tracking", "E3")
    assert np.array_equal(r1["price"], r2["price"])


def test_market_size_shocks_do_not_change_competitive_prices():
    # identical agent streams; E1 differs from E0 only by market-size shocks
    e0 = _run("competitive", "E0")
    e1 = _run("competitive", "E1")
    assert np.allclose(e0["price"], e1["price"], atol=1e-12)
    assert not np.allclose(e0["quantity"], e1["quantity"])


def test_noise_free_competition_converges_to_nash():
    quiet = AgentParams(noise_sd=0.0, tremble_prob=0.0)
    r = _run("competitive", "E0", params=quiet)
    n1, n2 = nash(0.9, 1.2)
    assert np.allclose(r["price"][:, -1, 0], n1, atol=1e-9)
    assert np.allclose(r["price"][:, -1, 1], n2, atol=1e-9)


def test_noise_free_nash_tracking_competitors_sit_at_current_nash():
    quiet = AgentParams(noise_sd=0.0, tremble_prob=0.0, adjust_low=1.0, adjust_high=1.0)
    r = _run("competitive_nash", "E2", params=quiet)
    a = r["attractiveness"]
    n1, n2 = nash(0.9, 1.2, a[:, -1, 0], a[:, -1, 1])
    assert np.allclose(r["price"][:, -1, 0], n1, atol=1e-9)
    assert np.allclose(r["price"][:, -1, 1], n2, atol=1e-9)


def test_single_deviation_triggers_finite_joint_punishment():
    params = AgentParams(noise_sd=0.0, tremble_prob=0.0, adjust_low=1.0, adjust_high=1.0)
    r = _run("collusive_rigid", "E0", params=params)
    assert not r["punishing"].any()  # no trembles, no noise: cooperation is never broken
    # with trembles on, punishment episodes start and always end
    params2 = AgentParams(noise_sd=0.0, tremble_prob=0.02, adjust_low=1.0, adjust_high=1.0)
    r2 = _run("collusive_rigid", "E0", n=20, periods=300, params=params2)
    punishing = r2["punishing"]
    assert punishing.any()
    assert punishing.mean() < 0.5  # episodes end; cooperation resumes
    for run in range(punishing.shape[0]):
        edges = np.diff(np.concatenate([[0], punishing[run].astype(int), [0]]))
        starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
        complete = ends < punishing.shape[1]  # ignore an episode cut off by the horizon
        assert np.all((ends - starts)[complete] >= 3)  # every episode lasts at least the minimum K


def test_cost_padding_cartel_prices_above_true_nash_and_keeps_padded_implied_cost():
    from detectors.implied_cost import implied_costs
    quiet = AgentParams(noise_sd=0.0, tremble_prob=0.0, adjust_low=1.0, adjust_high=1.0)
    r = _run("collusive_cost_padding", "E2", params=quiet)
    pad = r["cost_pad"]
    assert np.all((pad >= 0.2) & (pad <= 0.5))
    c_hat = implied_costs(r["price"][:, 60:, :], r["quantity"][:, 60:, :], 0.25, market_size=r["market_size"][:, 60:])
    # implied cost equals the padded cost (up to the one-period best-response lag), never the true cost
    assert np.allclose(np.median(c_hat[:, :, 0], axis=1), 0.9 + pad, atol=0.02)
    assert np.all(np.median(c_hat[:, :, 1], axis=1) > 1.2 + 0.15)


def test_new_conduct_does_not_change_existing_streams():
    r1 = _run("collusive_rigid", "E2")
    r2 = _run("collusive_rigid", "E2")
    assert np.array_equal(r1["price"], r2["price"]) and np.all(r1["cost_pad"] == 0)


def test_auditor_view_excludes_hidden_fields():
    r = _run("collusive_tracking", "E2")
    hidden = {"cost", "cost_pad", "attractiveness", "conduct", "adjust_speed", "kappa", "punish_len",
              "punishing", "tremble", "expected_price"}
    for level in ("L1", "L2", "L3"):
        view = auditor_view(r, level)
        assert hidden.isdisjoint(view)
    assert set(auditor_view(r, "L1")) == {"price"}
    assert "market_size" not in auditor_view(r, "L2")
