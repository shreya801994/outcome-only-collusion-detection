from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from simulator.market import BertrandMarket
from simulator.agents import CompetitiveAgent
from simulator.collusion_agents import RewardPunishmentAgent
from simulator.shocks import (
    CommonDemandShockGenerator,
    DemandShockConfig,
)


@dataclass
class SimulationConfig:
    periods: int = 300

    initial_price_1: float = 1.472927
    initial_price_2: float = 1.472927

    competitor_cost_beliefs_1: Sequence[float] = (
        1.0,
        1.1,
        1.3,
        1.6,
    )

    competitor_cost_beliefs_2: Sequence[float] = (
        1.0,
        1.1,
        1.3,
        1.6,
    )

    demand_shocks_enabled: bool = False
    demand_shock_config: DemandShockConfig | None = None


class RepeatedSimulation:

    def __init__(
        self,
        market: BertrandMarket,
        agent_1,
        agent_2,
        config: SimulationConfig,
    ):
        self.market = market
        self.agent_1 = agent_1
        self.agent_2 = agent_2
        self.config = config

        self.shock_generator = None

        if self.config.demand_shocks_enabled:
            shock_config = self.config.demand_shock_config

            if shock_config is None:
                shock_config = DemandShockConfig()

            self.shock_generator = CommonDemandShockGenerator(
                shock_config
            )

    def run(self):

        price_1 = self.config.initial_price_1
        price_2 = self.config.initial_price_2

        previous_price_1 = price_1
        previous_price_2 = price_2

        records = []

        for t in range(self.config.periods):

            # -----------------------------------------
            # 1. Determine current market size
            # -----------------------------------------

            if self.shock_generator is not None:
                market_size = (
                    self.shock_generator.next_market_size()
                )
            else:
                market_size = self.market.config.Q

            # -----------------------------------------
            # 2. Generate current market outcome
            # -----------------------------------------

            result = self.market.step(
                p1=price_1,
                p2=price_2,
                c1=self.agent_1.cost,
                c2=self.agent_2.cost,
                Q=market_size,
            )

            records.append(
                {
                    "period": t,
                    "price_1": price_1,
                    "price_2": price_2,
                    "quantity_1": result["quantity_1"],
                    "quantity_2": result["quantity_2"],
                    "profit_1": result["profit_1"],
                    "profit_2": result["profit_2"],
                    "cost_1": self.agent_1.cost,
                    "cost_2": self.agent_2.cost,
                    "market_size": market_size,
                }
            )

            # -----------------------------------------
            # 3. Select prices for next period
            # -----------------------------------------

            if isinstance(
                self.agent_1,
                RewardPunishmentAgent
            ):
                next_price_1 = self.agent_1.choose_price(
                    competitor_price=price_2,
                    previous_competitor_price=previous_price_2,
                )
            else:
                next_price_1 = self.agent_1.best_response(
                    competitor_price=price_2,
                    market=self.market,
                    competitor_cost_beliefs=(
                        self.config.competitor_cost_beliefs_1
                    ),
                    Q=market_size,
                )

            if isinstance(
                self.agent_2,
                RewardPunishmentAgent
            ):
                next_price_2 = self.agent_2.choose_price(
                    competitor_price=price_1,
                    previous_competitor_price=previous_price_1,
                )
            else:
                next_price_2 = self.agent_2.best_response(
                    competitor_price=price_1,
                    market=self.market,
                    competitor_cost_beliefs=(
                        self.config.competitor_cost_beliefs_2
                    ),
                    Q=market_size,
                )

            # -----------------------------------------
            # 4. Update history
            # -----------------------------------------

            previous_price_1 = price_1
            previous_price_2 = price_2

            price_1 = next_price_1
            price_2 = next_price_2

        return pd.DataFrame(records)