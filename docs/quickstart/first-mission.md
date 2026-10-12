<!-- Mirrored from https://docs.spacetraders.io/quickstart/first-mission -->

# First Mission

Faction contracts are a good way to earn credits and learn the basics of the game. Your starter contract will require you to mine an asteroid field and deliver the ores to a nearby waypoint.

## View Contracts

When you registered your agent, you were given a starter contract. If you don't have the contract ID, you can view your contracts again by sending the following request:

```bash
curl -X GET 'https://api.spacetraders.io/v2/my/contracts' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Contract Terms

Each contract will have a set of terms, which describe the requirements for completing the contract. For example, you may be required to deliver a specified amount of cargo to a destination waypoint.

Contracts have a deadline for accepting the contract, and the terms will have a deadline for when the delivery must be completed. If you fail to meet the deadline, the faction will revoke the contract reclaim any advance funds you received.

> **Note: Expired Contracts**
>
> If you've come back here after the contract has expired, you will not be able to accept the contract that was initially given to you, but you can request a new contract through the `negotiate/contract` endpoint.

### Optional: Negotiating a new contract

If you've come back here after the contract has expired, you can request a new contract through the `negotiate/contract` endpoint.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/negotiate/contract' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Accept your contract

On accepting a contract, you will receive a small portion of the credits up front and the final amount on delivery. To accept your contract, send the following request:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/contracts/:contractId/accept' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

Don't stress too much about the details of the contract for now. If the contract is too difficult, you can always let the contract expire and accept a new one, or start a new agent and try again. Use the starter contract as an opportunity to learn the basics of the game.

To complete the contract, you will need to buy a ship, navigate your ship to an asteroid field, extract ores until your cargo hold is full, and deposit the contract ores at the delivery waypoint. The remaining ores can be sold at a marketplace for a profit (or jettisoned into space while still at the asteroid field if you want to fill up on only contract cargo).
