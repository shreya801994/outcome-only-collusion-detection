from dataclasses import dataclass


@dataclass
class RewardPunishmentAgent:
    cost: float
    high_price: float = 1.90
    punishment_price: float = 1.10
    deviation_tolerance: float = 0.05
    punishment_periods: int = 5

    def __post_init__(self):
        if self.punishment_periods <= 0:
            raise ValueError(
                "punishment_periods must be positive"
            )

        self.punishment_remaining = 0
        self.in_punishment = False

    def choose_price(
        self,
        competitor_price: float,
        previous_competitor_price: float,
    ) -> float:

        # Already inside a punishment episode.
        if self.in_punishment:

            self.punishment_remaining -= 1

            if self.punishment_remaining == 0:

                self.in_punishment = False

            return self.punishment_price

        # Detect a downward deviation.
        deviation = (
            previous_competitor_price
            - competitor_price
        )

        if deviation > self.deviation_tolerance:

            self.in_punishment = True

            # Current call counts as punishment period 1.
            self.punishment_remaining = (
                self.punishment_periods - 1
            )

            return self.punishment_price

        return self.high_price

    def reset(self):
        self.punishment_remaining = 0
        self.in_punishment = False