from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import minimize_scalar

from simulator.market import BertrandMarket


@dataclass
class CompetitiveAgent:
    cost: float
    firm_id: int
    price_min: float = 0.5
    price_max: float = 4.0

    def best_response(
        self,
        competitor_price: float,
        market: BertrandMarket,
        competitor_cost_beliefs: Sequence[float],
        belief_probabilities: Sequence[float] | None = None,
        Q: float | None = None
    ):
        beliefs = np.asarray(
            competitor_cost_beliefs,
            dtype=float
        )

        if len(beliefs) == 0:
            raise ValueError(
                "competitor_cost_beliefs cannot be empty"
            )

        if belief_probabilities is None:
            probabilities = np.ones(len(beliefs)) / len(beliefs)
        else:
            probabilities = np.asarray(
                belief_probabilities,
                dtype=float
            )

            if len(probabilities) != len(beliefs):
                raise ValueError(
                    "Beliefs and probabilities must have the same length"
                )

            if np.any(probabilities < 0):
                raise ValueError(
                    "Belief probabilities cannot be negative"
                )

            probability_sum = probabilities.sum()

            if probability_sum <= 0:
                raise ValueError(
                    "Belief probabilities must sum to a positive value"
                )

            probabilities = probabilities / probability_sum

        def expected_negative_profit(price):
            expected_profit = 0.0

            for competitor_cost, probability in zip(
                beliefs,
                probabilities
            ):
                if self.firm_id == 1:
                    profit, _ = market.profits(
                        p1=price,
                        p2=competitor_price,
                        c1=self.cost,
                        c2=competitor_cost,
                        Q=Q
                    )
                else:
                    _, profit = market.profits(
                        p1=competitor_price,
                        p2=price,
                        c1=competitor_cost,
                        c2=self.cost,
                        Q=Q
                    )

                expected_profit += probability * profit

            return -expected_profit

        result = minimize_scalar(
            expected_negative_profit,
            bounds=(self.price_min, self.price_max),
            method="bounded"
        )

        if not result.success:
            raise RuntimeError(
                f"Best-response optimization failed: {result.message}"
            )

        return result.x