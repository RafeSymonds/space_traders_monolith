<!-- Mirrored from https://docs.spacetraders.io/game-concepts/markets -->

# Markets

## Overview

Markets in SpaceTraders are driven by supply and demand. Marketplaces will list of goods for trade that are either imports, exports, or exchange goods.

Exports are goods produced at the waypoint, and typically have a lower purchase price than import goods. Import goods are consumed at the waypoint, and typically have a higher sell price.

Buying at places that export goods, and selling at waypoints that import them will typically be the most profitable way to earn credits in SpaceTraders.

```bash
curl -X GET 'https://api.spacetraders.io/v2/systems/:systemSymbol/waypoints/:waypointSymbol/market'
```

## Visibility

Price data and transaction history are only available if you have a ship located at the waypoint. It is common to send cheap probe ships into orbit around a waypoint to gather and monitor market data.

Having visibility into market data over time can be highly profitable. You can use this data to predict the future price of goods and plan your trade routes accordingly.

## Exports

Exports are goods produced over time by the waypoint where the good is listed.

The purchase price of an export good tends to decrease over time as supply naturally increases from production. As agents buy up supply from an export good, production tends to increase to meet the demand. Be careful though, as this can only happen when there is an adequate supply of imports.

Exports are constrained by the supply of imports. When a market has an unmet need for the imports that are necessary to produce an export, production for export goods will be constrained, leading to a slower decrease in export prices.

## Imports

Imports are goods consumed over time by the civilization where the good is listed.

The sell price of an import good tends to increase over time as supply naturally decreases from consumption. As agents supply more of an import good, consumption will typically increase as the price for that good goes down.

**Future**: If a waypoint has an unmet supply for their imports, it can contribute to instability and potentially cause a collapse of the market. This can lead to increased piracy in the system, making it more dangerous for agents to trade and exchange goods.

## Exchange goods

Another type of market listing includes exchange goods. These goods are neither consumed nor produced at the waypoint. Instead, they are traded strictly among agents.

The price of an exchange good fluctuates purely based on supply and demand driven by agents.

## Commodity goods

Fuel is the most common exchange good listed across markets. Fuel is consumed by agents to travel between waypoints, which means there is always a natural demand for the good.

The price of fuel can skyrocket at popular locations with high demand, but where players aren't providing enough supply. Replenish the fuel at waypoints by siphoning the gas giants around the system, and bringing the hydrocarbons to a refinery.

## Growing markets

Smaller civilizations typically start with a limited number of basic goods in their markets. As agents trade and exchange goods, these markets will slowly grow.

**Future**: As agents trade and exchange goods, the market will grow and trigger the introduction of new types of goods.

More advanced systems will typically export higher technology and more advanced goods, but in turn have a higher demand for goods that must be met by agents.

**Future**: Failing to meet the demand for commodity goods can cause the market to collapse.

Maintaining a healthy market is a key part of maximizing profitability for agents. Markets that are well supplied tend to offer much more consistent margins on goods, but they require more attention to maintain.
