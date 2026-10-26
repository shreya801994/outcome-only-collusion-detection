from dataclasses import dataclass

import numpy as np


@dataclass
class AdaptiveCompetitiveAgent:
    cost: float
    firm_id: int

    base_price: float = 1.472927
    reference_market_size: float = 1.0

    shock_sensitivity: float = 0.50
    adjustment_speed: float = 0.40

    noise_std: float = 0.01

    price_min: float = 0.5
    price_max: float = 4.0

    seed: int | None = None

    def __post_init__(self):

        if not 0.0 < self.adjustment_speed <= 1.0:
            raise ValueError(
                "adjustment_speed must be between 0 and 1"
            )

        if self.noise_std < 0:
            raise ValueError(
                "noise_std cannot be negative"
            )

        self.rng = np.random.default_rng(
            self.seed
        )

        self.current_price = self.base_price

    def target_price(
        self,
        market_size: float,
    ) -> float:

        market_change = (
            market_size
            - self.reference_market_size
        )

        target = (
            self.base_price
            + self.shock_sensitivity
            * market_change
        )

        return target

    def choose_price(
        self,
        market_size: float,
    ) -> float:

        target = self.target_price(
            market_size
        )

        adjustment = (
            self.adjustment_speed
            * (
                target
                - self.current_price
            )
        )

        noise = self.rng.normal(
            loc=0.0,
            scale=self.noise_std,
        )

        new_price = (
            self.current_price
            + adjustment
            + noise
        )

        new_price = max(
            self.price_min,
            min(
                self.price_max,
                new_price,
            ),
        )

        self.current_price = new_price

        return new_price

    def reset(self):

        self.current_price = (
            self.base_price
        )