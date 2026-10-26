from dataclasses import dataclass

import numpy as np


@dataclass
class DemandShockConfig:
    base_market_size: float = 1.0
    shock_probability: float = 0.10
    positive_shock: float = 0.20
    negative_shock: float = -0.20
    seed: int = 42


class CommonDemandShockGenerator:
    def __init__(self, config: DemandShockConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)

    def next_market_size(self):
        draw = self.rng.random()

        if draw < self.config.shock_probability / 2:
            shock = self.config.positive_shock

        elif draw < self.config.shock_probability:
            shock = self.config.negative_shock

        else:
            shock = 0.0

        return self.config.base_market_size * (1.0 + shock)