from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize_scalar

from simulator.market import BertrandMarket


@dataclass
class ReactiveCompetitiveAgent:
    cost: float
    firm_id: int
    response_strength: float = 0.50
    adjustment_speed: float = 0.40
    noise_std: float = 0.01
    price_min: float = 0.5
    price_max: float = 4.0
    reaction_threshold: float = 0.05
    seed: int | None = None

    def __post_init__(self):
        if self.cost < 0:
            raise ValueError("cost cannot be negative")

        if self.firm_id not in (1, 2):
            raise ValueError("firm_id must be 1 or 2")

        if not 0.0 <= self.response_strength <= 1.0:
            raise ValueError(
                "response_strength must be between 0 and 1"
            )

        if not 0.0 < self.adjustment_speed <= 1.0:
            raise ValueError(
                "adjustment_speed must be between 0 and 1"
            )

        if self.noise_std < 0:
            raise ValueError(
                "noise_std cannot be negative"
            )

        if self.reaction_threshold < 0:
            raise ValueError(
                "reaction_threshold cannot be negative"
            )

        self.rng = np.random.default_rng(self.seed)

        self.current_price = None

    def competitive_best_response(
        self,
        competitor_price: float,
        market: BertrandMarket,
        Q: float = 1.0,
    ) -> float:

        def negative_profit(price):

            if self.firm_id == 1:
                profit, _ = market.profits(
                    p1=price,
                    p2=competitor_price,
                    c1=self.cost,
                    c2=self.cost,
                    Q=Q,
                )
            else:
                _, profit = market.profits(
                    p1=competitor_price,
                    p2=price,
                    c1=self.cost,
                    c2=self.cost,
                    Q=Q,
                )

            return -profit

        lower_bound = max(
            self.price_min,
            self.cost,
        )

        if lower_bound >= self.price_max:
            lower_bound = self.price_min

        result = minimize_scalar(
            negative_profit,
            bounds=(lower_bound, self.price_max),
            method="bounded",
        )

        if not result.success:
            raise RuntimeError(
                f"Best-response optimization failed: "
                f"{result.message}"
            )

        return float(result.x)

    def choose_price(
        self,
        competitor_price: float,
        previous_competitor_price: float,
        market: BertrandMarket,
        Q: float = 1.0,
    ) -> float:

        if self.current_price is None:
            self.current_price = self.competitive_best_response(
                competitor_price=competitor_price,
                market=market,
                Q=Q,
            )

        competitor_change = (
            competitor_price
            - previous_competitor_price
        )

        competitive_target = self.competitive_best_response(
            competitor_price=competitor_price,
            market=market,
            Q=Q,
        )

        reaction_target = competitive_target

        if competitor_change < -self.reaction_threshold:

            reactive_target = (
                self.current_price
                + self.response_strength * competitor_change
            )

            reaction_target = (
                (1.0 - self.response_strength)
                * competitive_target
                + self.response_strength
                * reactive_target
            )

        adjustment = self.adjustment_speed * (
            reaction_target - self.current_price
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
            min(self.price_max, new_price),
        )

        self.current_price = new_price

        return new_price

    def reset(self):
        self.current_price = None