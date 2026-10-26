from dataclasses import dataclass
import numpy as np


@dataclass
class MarketConfig:
    Q: float = 1.0
    a0: float = 0.0
    a1: float = 2.0
    a2: float = 2.0
    mu: float = 0.25


class BertrandMarket:

    def __init__(self, config: MarketConfig):
        self.config = config

    def demand(self, p1: float, p2: float, Q: float | None = None):
        if Q is None:
            Q = self.config.Q

        a0 = self.config.a0
        a1 = self.config.a1
        a2 = self.config.a2
        mu = self.config.mu

        u0 = a0 / mu
        u1 = (a1 - p1) / mu
        u2 = (a2 - p2) / mu

        maximum = max(u0, u1, u2)

        e0 = np.exp(u0 - maximum)
        e1 = np.exp(u1 - maximum)
        e2 = np.exp(u2 - maximum)

        denominator = e0 + e1 + e2

        q1 = Q * e1 / denominator
        q2 = Q * e2 / denominator

        return q1, q2

    def profits(
        self,
        p1: float,
        p2: float,
        c1: float,
        c2: float,
        Q: float | None = None
    ):
        q1, q2 = self.demand(p1, p2, Q)

        profit1 = (p1 - c1) * q1
        profit2 = (p2 - c2) * q2

        return profit1, profit2

    def step(
        self,
        p1,
        p2,
        c1,
        c2,
        Q: float | None = None
    ):
        q1, q2 = self.demand(p1, p2, Q)

        profit1 = (p1 - c1) * q1
        profit2 = (p2 - c2) * q2

        if Q is None:
            Q = self.config.Q

        return {
            "price_1": p1,
            "price_2": p2,
            "quantity_1": q1,
            "quantity_2": q2,
            "profit_1": profit1,
            "profit_2": profit2,
            "market_size": Q
        }