from simulator.market import BertrandMarket, MarketConfig


def test_demand_is_positive():

    market = BertrandMarket(MarketConfig())

    q1, q2 = market.demand(1.47, 1.47)

    assert q1 > 0
    assert q2 > 0


def test_total_demand_does_not_exceed_market_size():

    market = BertrandMarket(MarketConfig())

    q1, q2 = market.demand(1.47, 1.47)

    assert q1 + q2 <= market.config.Q


def test_symmetric_firms_have_equal_demand():

    market = BertrandMarket(MarketConfig())

    q1, q2 = market.demand(1.47, 1.47)

    assert abs(q1 - q2) < 1e-10

def test_market_quantity_scales_with_market_size():
    market = BertrandMarket(MarketConfig())

    q1_small, q2_small = market.demand(
        p1=1.472927,
        p2=1.472927,
        Q=0.8
    )

    q1_large, q2_large = market.demand(
        p1=1.472927,
        p2=1.472927,
        Q=1.2
    )

    assert q1_large > q1_small
    assert q2_large > q2_small