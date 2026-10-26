from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent
from simulator.simulation import RepeatedSimulation, SimulationConfig


market = BertrandMarket(MarketConfig())

agent_1 = CompetitiveAgent(
    cost=1.0,
    firm_id=1
)

agent_2 = CompetitiveAgent(
    cost=1.0,
    firm_id=2
)

config = SimulationConfig(
    periods=300
)

simulation = RepeatedSimulation(
    market=market,
    agent_1=agent_1,
    agent_2=agent_2,
    config=config
)

data = simulation.run()

print(data.head())
print()
print("Number of periods:", len(data))
print()
print("Average prices:")
print(data[["price_1", "price_2"]].mean())
print()
print("Average quantities:")
print(data[["quantity_1", "quantity_2"]].mean())
print()
print("Average profits:")
print(data[["profit_1", "profit_2"]].mean())

data.to_csv(
    "data/competitive_baseline.csv",
    index=False
)

print()
print("Saved to data/competitive_baseline.csv")