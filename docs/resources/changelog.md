<!-- Mirrored from https://docs.spacetraders.io/resources/changelog -->

# Changelog

This is a list of all the changes made to the game. We will try to keep this
list up to date with the latest changes, but it may not always be accurate. If
you have any questions, please ask in the `#general-chat` channel on Discord.

---

## March 23, 2025

This reset focuses on system generation. There's no changes to functionality, but I've tweaked the generation parameters of the universe again to make non-home and starter systems more likely to be, well, awesome.

- TIer 5 systems are now a thing. I'm fairly sure nobody knew systems had tiers, but Galactic Inc. has been classifying them as such for quite a while. Home systems are not the best systems in the universe any more. There's better systems out there now, go find them.
- Every planet now has a chance to be populated
- Every populated planet now needs some minimal goods to keep it's population fed and happy (actually, I'm fairly certain none of the planetary governments care about the happiness of the populace, but at least they import the required goods).
- (Populated) Planets have a much higher chance to have a station which sells ships. Surprisingly enough people do not enjoy the idea of being stranded in an intergalactic society).
- Astronomers have discovered that planets have moons, even outside the starting systems.
- Gas giants are especially prone to having moons due to their size.
- The factions aren't somehow spread throughout the entire galaxy, their influence extends in a more natural manner
- To promote efficient use of resources, management has decided to significantly reduce jump lane numbers and length, to compensate, you will be given more efficient reactors, that won't need to cool down quite so long.
- Because that same management couldn't figure out how to pronounce `X1-XDFS-DMEP`, systems can now be referred to by alternative names, like `Omicron Alpha I`, their new properties include `constellation` and `name` on the `System` entity.
- It has been discovered that the reason systems were underdeveloped was because they had no jump gates, and it was hard to cart resources there using warp, therefore, more jump gates have been built all across the galaxy.
- To prevent mere paupers from overrunning the elite faction home system, starting systems have been spread out (any issues you have with placement can be directed towards the planning committee).

## February 27, 2025

Added ship module installation and removal endpoints, following the same pattern as ship mounts. This allows players to modify their ships' capabilities by installing and removing modules at shipyards.

**BREAKING CHANGES**

- Ship nav mode can now be updated in transit. This will cost additional fuel, but will make your ship arrive faster when the nav mode is changed to a faster speed. Unfortunately, switching to a slower speed does not return fuel that was already spent (and the endpoint will throw an error if you try to do so). Due to this, the ship nav patch endpoint now returns both nav and fuel objects (same as the navigate endpoint), not just the nav object at top level.

**Updates**

- Added new endpoints for managing ship modules:

  - GET `/my/ships/{shipSymbol}/modules` to list installed modules
  - POST `/my/ships/{shipSymbol}/modules/install` to install a module
  - POST `/my/ships/{shipSymbol}/modules/remove` to remove a module
- Added new error codes for module-related operations:

  - 4266: Ship Module No Shipyard Error
  - 4267: Ship Module Not Installed Error
  - 4268: Ship Module Insufficient Credits Error

**Documentation**

- Added OpenAPI specifications for the new module endpoints

**Changes**

- Gave the shuttle a faster engine to give it some role in the game (as opposed to the default light freighter).
- Increased the relative speed of the slowest engines significantly to make mistakes less painful. Need to see how this works out, as it might make drift potentially very powerful for probes.
- Tweaked the relative spawn chance of randomly generated ship types to make the rare ones a bit more likely to show up (note that this means they exist about 5 times in the inner, and 10 times in the outer galaxy).
- Added a new ship type, which you'll need to find by exploring the galaxy. It uses a never before seen module (I think).
- Some modifications have been made to the seeding logic for waypoints to ensure that most imports in a system have a source (either in the same system, or in a neighbor).

## January 25, 2025

Added an agent dashboard to the game. You can use this to register new agents and get tokens.

Registering a new account won't happen automatically though the register endpoint any more, you'll need to register an account through the dashboard, and either use the dashboard, or the register endpoint with a new 'account' token to create a new agent.

**Updates**

- Added an agent dashboard to the game. You can use this to register new agents and get tokens.

---

## January 22, 2025

Fixed a little bit in the seeding.

**Fixes**

- JumpGate Connections don't "self link" anymore.
- HQ's dont get reduced to StarterSystems anymore

## March 24, 2024

Only some minor updates this week and we'll be fairly busy this month, but will
be working on a surprise feature in the near future. We don't have an estimate
on when this feature will be ready, but we are aiming for the next reset or the
following reset.

**Updates**

- lowered the cost of repairing ships while we work on adjusting ship prices in
  general to take into account the new repair and scrap systems
- lowered the credits given for scrapping a ship

---

## March 10, 2024

We are bumping the release from v2.1 to v2.2 with some changes to implement ship
condition and adverse ship events. With this release comes some new endpoints to
repair and scrap ships, a change to the properties of ship components (frame /
reactor / engine), and a new key for `events` when navigating and extracting.

This is just an initial release of this new game mechanic, and we will be
tweaking the balance of ship condition and adverse ship events over the next few
resets. A lot of the balance will depend on how players respond to these new
mechanics, so we will be watching closely and making adjustments as needed
(potentially mid-reset if needed).

**Breaking Changes**

- the `condition` property has been updated from an integer to a float between 0
  and 1. Previously the condition property wasn't being used, but now it will
  be used to determine the health of the ship. The condition will degrade over
  time and with adverse ship events, and players will need to repair their ships
  to keep them in good condition.

**Updates**

- added new endpoints to repair and scrap ships with credits based on the
  condition of the ship, and the price of materials at the shipyard.
- ships will perform worse when their condition is low, but will never become
  inoperable to allow new players to ignore this mechanic if they choose.
- ship components now have an `integrity` property that will degrade with each
  repair to the ship, representing the long-term health of the ship. The
  integrity of a ship component is non-repairable and will eventually require
  the ship to be scrapped.
- aded a new key for `events` to several endpoints that will detail any adverse
  ship events that have occurred to the ship. This will be used to determine
  when the condition of the ship degrades, and will be used in the future for
  other adverse ship events. Only navigation and extraction will return events
  for now, but we will add more events in the future.

---

## February 25, 2024

No updates this reset but we are testing a release that will add adverse ship
events to the game which will degrade ship condition, and require players to
repair or scrap their ships. Responses such as navigate and extract will now
return an events property that will detail any adverse events that have occurred
to the ship.

We weren't able to finalize this in time, but it will be ready to go for the
next reset.

---

## February 10, 2024

A few minor fixes this reset but no major changes. The team is still a bit busy
with other commitments but have been doing a lot of thinking / planning around
what the next major release will look like. We might also be tackling actual
accounts soon and a simple authentication system.

**Fixes**

- fixed an exploit that would allow an agent to accept / fulfill a contract more
  than once.
- added missing exports for biocomposites and lab instruments to starter systems
  to further fill out the supply chain.
- fixed a bug where each starting system was supposed to have a unique export / import
  connected to other starting systems, but this was not the case.
- tweaked imports for quantum stabilizers and quantum drives to remove uranite / meritium

---

## January 13, 2024

Note: we will be moving resets to Sundays instead of Saturdays in the future.

No major updates this reset. We fixed a bug in the last two resets with trade
volumes being set too high across all systems. More advanced goods have a lower
trade volume cap than raw resources.

With this fix there will likely be a slower ramp up period and we may need to
continue to tweak these numbers.

Other than that, our day jobs have kept us fairly busy this week so we don't
have any other updates. We are thinking about the next minor release and
planning a re-working of the docs website to improve the getting started
experience.

**Updates**

- trade volumes are now properly enforced as intended for various types of
  goods, and starting systems have the most reserved caps for how big a market
  will grow. Ships and advanced goods have the lowest caps, and raw resources
  have the highest.

---

## December 16, 2023

We had some down time these past two weeks due to illness, so not too many updates
on this reset. There are a few bug fixes and some breaking changes based on
feedback and a deprecated property.

This week we want to slow down the economy a bit relative to how quickly things
progressed on the last reset, so some of the market production / consumption has
been tweaked. Each system also has a min / max trade volume for certain goods,
and we are still working on exposing properties to help players understand how
this works. Starting systems are tier 1, and so will cap early, but you can find
other markets that have higher limits.

If things continue to go well we might start working on another larger feature
(TBD) after wrapping up any final bug fixes and doc updates.

**Breaking Changes**

- removed deprecated property `departure` on ShipNavRoute. If you are still
  using this property, switch to the new `origin` property which replaces the
  use of `departure`.
- the GET construction endpoint now returns a 200 instead of a 404 for waypoints that
  are not under construction.

**Updates**

- slightly slowed down production / consumption of goods at markets to extend
  the early stages of the game
- updated the min / max range of trade volumes across the markets based on the
  system tier (which is still an internal flag and will be exposed soon)
- added agent to the jump ship response as credits are deducted on a jump
- added symbol property to the jump gate object
- slightly increased the materials cost of jump gate construction

**Bug Fixes**

- fixed missing antimatter for some jump gates causing ships to get stranded

---

## December 2, 2023

No major changes this week due to Thanksgiving break and being a bit busy with
work. We fixed a few bugs and tweaked a few parameters on market growth.

**Updates**

- updated ActivityLevel to RESTRICTED only when there is a supply issue between
  imports / exports. Previously this flag would be set when either supply is
  limited OR the market can't grow due to import-to-export ratios. A new,
  separate flag will be added to indicate that a market can't grow because the
  related import / export market is too small.
- lowered max trade volume from 600 to 400 for starter systems. Internally each
  system has a tier (this will be exposed soon) which limits how big markets can
  get. Home systems and others have higher limits than the starting system.
- increased the minimum trade volume of some markets that might provide some early price stability in trades
- also increased exchange trade volume from 100 to 300 to provide a little more price stability
- slightly increased growth of market production / consumption relative to supply levels
- slightly decreased market sensitivity to supply levels for market growth
- slightly decreased sensitivity RESTRICTED Activity Level relative to supply levels
- lowered construction requirement of FAB_MATS and increased requirement of ADVANCED_CIRCUITRY

**Bug Fixes**

- fix bug where refueling from cargo wouldn't remove cargo
- fix bug where refueling worked when fuel wasn't available at the market
- fixed a bug where market production / consumption would drop because it
  couldn't "grow" to the next trade volume, when the intention was it should
  only drop when related import / export supplies hit extremes
- fixed a bug where supply levels can get very high or very low, and when
  markets decline it makes it very hard to re-balance the supply. Market
  declines should no longer result in very extreme supply scenarios.

---

## November 18, 2023

This week's reset brings a number of changes and fixes aimed at balancing the
in-game economy. We will continue to monitor the economy and make adjustments
as needed. With these changes, you may notice that your economy stalls out
pretty early if you aren't supplying markets with raw materials.

The reset schedule will continue to be every two weeks. We may apply some
mid-reset adjustments to the economy as needed. For the next two weeks we will
continue to monitor the economy and focus on some bug fixes and deprecations to
the API.

**Updates**

- Market Growth Fix: Resolved a persistent issue where the markets for ship
  parts and ship plating would expand indefinitely, regardless of the actual
  demand for ships.
- Market Rebalance and New Activity Level: We've adjusted the market dynamics to
  prevent trade goods from exceeding their related imports/exports, which
  previously led to overly simplified and highly profitable trade loops. A new
  Activity Level, "RESTRICTED," has been introduced. This level indicates supply
  chain issues for related imports/exports. For instance, a "RESTRICTED" status
  on IRON export implies a shortage in IRON ORE import, affecting IRON
  production. Supplying the necessary IRON ORE will resolve this restriction.
- New Pirate Base: A pirate base has been added in the outer asteroid belt. This
  base has demand for weapons, but you wouldn't want to trade with pirates, would you?
- Refueling Update: players can now refuel from cargo by setting `fromCargo: true` in your request (thanks Feba!).
- Jump Gate Construction Cost Reduction: The cost of Fabrication Materials
  (FAB_MAT) for constructing jump gates has been lowered, hopefully making interstellar
  travel more accessible.
- New Shuttle Ship in Starting System: A more affordable trading ship is
  now available in the starting system, ideal for short-range trading.
- Fuel and Trade Good Adjustments: We've reduced the cost of fuel and
  tweaked the base price of several trade goods, as well as some of the import
  / export mapping.
- Cargo Hold Capacity Changes: Cargo storage capacity has been slightly
  increased for tier I and II cargo holds, while it has been marginally reduced
  for tier III holds, balancing the storage capabilities across different tiers.
- Enhanced Asteroid Mining: The extraction limit for engineered asteroids has been
  increased from approximately 10 to around 20 extractions per minute, boosting
  mining efficiency and resource availability.

---

## November 4, 2023

This week we are rebalancing some of the markets in the starting systems to
provide a full supply chain of goods. That means prices have changed quite a bit
so you'll want to check the new prices before you start trading.

This week was mostly focused on bug fixes and rebalancing from the v2.1 release.
We'll switch to a forthnightly reset schedule starting this week, and will start
planning what features are going into the v2.2 release.

For the next few resets we'll mostly be working on the Playground to make it
fully functional, and update the quickstart to add some visual elements to help
new players get started.

**Bug Fixes**

- jump gates should now always have connections, and each starter system should
  have a connection to the faction headquarters system.
- fixed a memory leak with the websocket server
- we will patch the construction supply endpoint to prevent an edge case where a
  race condition can lead to negative cargo.
- fix an issue where a "full cargo" error was thrown when an extraction resulted
  in 0 yield.
- fixed an issue where all yields were coming out as iron ore
- fixed an issue where export markets wouldn't grow when imports were going
  strong and trade activiy was high.
- fixed some factions being marked as `isRecruiting` when they are in fact not
  recruiting.

**Updates**

- a new trade good FAB_MAT has been added as a general construction material
- jump gate construction has been updated to replace Platinum with Fabrication
  Materials and other more common goods
- prices have been adjusted to generally balance imports to exports, resulting
  in a number of trade goods going up in price. One impact of this change is
  that ships are more expensive, but the margin on trading should be high enough
  to make these ships more affordable.
- coming soon will be system tiers that limit the size of markets in a system,
  and starter systems will have a cap. There may be a feature in the future to
  help upgrade these systems to higher tiers.

---

## v2.1 Release

This week we've released v2.1 which includes a few breaking API changes, a
number of tweaks to gameplay, and a reworking of the universe seeder, including
what your faction starting system looks like.

Over the next few weeks we'll be playtesting and tweaking the new mechanics to
make sure the game is balanced and fun. Check the updates below to learn more
about what's new in v2.1.

- if you notice any bugs or exploits, please let us know in Discord. We really
  appreciate the help in finding these issues! We expect to need to rebalance
  the economy a few times over the next few weeks as everyone playtests the new
  mechanics.
- if you find any errors that don't have codes, please let us know so we can add
  them to the documentation.
- we'll be pushing regular updates to the new [Playground](https://docs.spacetraders.io/playground) to support all of the
  basic gameplay mechanics. We'll also be adding more documentation to the API
  docs to help new players get started.

**Gameplay Updates**

- the asteroid field waypoint has been replaced with **individual asteroids**, and
  each asteroid now has an extraction rate limit before it becomes unstable.
  That means you can't just mine the same asteroid over and over again.
  Eventually we'll add some way of ballparking the rate limit, but for now you
  can assume about 10 extractions per minute before you risk the asteroid
  becoming unstable.
- **starting system** markets now start begin low trade volume, and will increase
  over time as players trade with the market. This means you'll want to trade
  consistently with the market to promote growth. A new enum for ActivityLevel
  has been added to each trade good in the market, which will tell you how
  healthy the trade good is at that market.
- **fuel** is being tweaked to become more of a focus to maintain your fleet. We've
  made fuel a bit more scarce and decreased the fuel capacity of smaller ships.
  Players will want to make regular runs to gas giants to siphon fuel, or buy
  hydrocarbons and supply them to the local refinery to promote fuel exports.
- players can now **siphon** hydrocarbons from gas giants using the new siphon ship
  and gas processor module. Use the new siphon endpoint to siphon gases from a
  gas giant. Surveys are not part of this mechanic, so siphoning is fairly
  straight forward.
- **optimized cargo modules** have been added so that your ships can carry more
  cargo with the new modules, with the intention to make freighters and haulers
  more useful.
- the systems seeder has been completely rewritten and the code cleaned up. Many
  of the systems have a focus (mining, refining, manufacturing, etc) and we'll
  be able to continue to make systems more interesting over time. This release
  focused mostly on making the starting systems a little more interesting.
- **jump gates** have been reworked to have direct connections to other jump gates.
  This means you can't jump to a system that doesn't have a jump gate (use a
  warp drive if you want to explore systems without jump gates). Ships will
  still enter a cooldown after a jump based on distance, to prevent players from
  jumping too far too quickly. We might add multiple jump gates per system with
  unique connections in the future.
- waypoints now have **modifiers**, which are temporary conditions that affect the
  waypoint. For example, an asteroid can become "unstable" which makes
  extracting from it more difficult. We'll be adding more modifiers in the
  future.
- jumping from a jump gate now requires a unit of **antimatter** purchased from the
  market. Players will have to keep these markets supplied or the price of
  jumping will increase over time.
- we've added **websockets** to the API but have not documented these yet. The
  Playground uses these websockets to subscribe to departures in the system,
  showing your ships and others as they travel around. We'll be adding more
  events to the websockets in the future and documenting them. Right now the
  websockets are experimental and may be unstable.
- waypoints can now be **under construction** and players can supply the
  construction with materials using the new endpoint. Right now only jump gates
  are under construction, and we'll expand on this mechanic in the future.
- ship endpoints were previously "locked" on all requests, but will now only be
  locked on non-GET requests.
- we've added some **query filters** to the system waypoints endpoint so you can filter by
  waypoint type and traits. There are now far more waypoints per system than
  before, so you may need to use these filters or get comfortable with
  pagination to find what you're looking for.
- a new **survey ship** has been added to the game, with no new changes to how
  surveying works.

**API Updates**

- added new endpoints for `/construction` and `/construction/supply` to help
  complete waypoints that are under construction
- added new endpoints for `/my/ships/{shipSymbol}/siphon` to siphon gases from
  gas giants
- added some new enum values to WaypointTrait, ShipType, ShipModule,
  ActivityLevel, SupplyLevel
- added supply and activity enums to ShipyardShip and MarketTradeGood
- added new query filters to `/systems/{symbol}/waypoints` to filter by type and
  traits
- added `cooldown` to the `/my/ships/{shipSymbol}/jump` response

**Breaking Changes - Game Mechanics**

- **asteroids** are now individual waypoints, and asteroids have a rate limit before
  they become unstable. We'll be tweaking this new mechanic with playtesting,
  but for now you can assume about 10 extractions per minute before the asteroid
  becomes unstable. You can check waypoint modifiers to determine when you are
  exceeding a stable extraction rate, where you will first see "CRITICAL_LIMIT"
  warning you to reduce your extraction rate, and then "UNSTABLE" when you have
  exceeded the extraction rate and the asteroid is unstable.
- previously asteroids had consistent yields based on the waypoint traits, but
  now some yields are more likely than others (still based on the traits). That
  means each asteroid will have a **unique composition** of yields, which will make
  it more interesting to find the best asteroids to mine. We plan to also
  exhaust asteroids in the future.
- agents now start in a **random starting system** when they join a faction, and
  each starting system is roughly the same. You will need to complete the jump
  gate in your system if you want to travel to other systems, including the
  connected home system for your faction. Each starting system has some unique
  imports and exports, and the faction home system has better ships and mountsq
  available for purchase.

**Breaking Changes - API**

- the following modules have been removed: JUMP_DRIVE_I, JUMP_DRIVE_II,
  JUMP_DRIVE_III
- the following waypoint type is now deprecated: ASTEROID_FIELD
- jump gates now have direct connections to other jump gates

---

## October 15, 2023

Hello everyone! No change this week but we are getting closer on the v2.1 release which introduces a lot of interesting changes for you to play with. Below we've outlined some goals and the list of changes that should be making it into the next release.

We may push to send this out even if we're only 90% of the way there, so expect some bugs during that first reset. If you have any notes or suggestions, feel free to jump into Discord and let us know.

**Goals**

Here are some of the goals we are trying to achieve with the v2.1 release:

- extend the lifecycle of the reset into two weeks by slowing down the ramp up period in the starting system
- encourage players to explore outside their starting system by nerfing some of the starting resources and create new opportunities in the sector
- provide new players with an easy goal that is achievable within the first few days: constructing a jump gate that allows you to exit the system
- build a visualization UI for the docs that allows new players to understand the mechanics of the game and see what their ships are doing
- incorporate feedback and balance some mechanics of the game

**New Agent**

- starting a new agent will likely have a mix of different starting ships and credits,
  so expect that response type to change slightly
- we will update the quickstart and documentation to reflect the new starting
  resources

**Starter Systems**

- players will now start in a random system near the headquarters of their starting faction
- starting systems will have limited access to ship types, mounts and modules - your first goal should be to reach your jump gate and make it to the faction headquarters, where you can purchase better ships
- your jump gate in the starting system will be under construction (more below), so you will need to supply the required materials in order to start making jumps

**Mining And Asteroids**

- breaking change: the asteroid field waypoint type no longer exists, and is being replaced with individual asteroids
- systems are now seeded with dozens of asteroids in a belt, often an inner belt and an outer belt
- each asteroid has a unique mix of richer deposits of 2-3 resources, so it is worth extracting from each one to learn what the composition is - for example, you may find an asteroid out there richer in diamonds or other profitable resources.
- asteroids will now enter an unstable state if they are over-extracted in a given period, which will result in significantly reduced yields during that time

  - this period of instability will eventually self-correct, and yields will return to normal
  - check the new modifiers property on the asteroid and keep an eye on the "critical limit" modifier, which indicates that the asteroid is about to become unstable.
  - decrease your rate of mining on the asteroid until you find a stable rate of
    extraction

**Waypoint Modifiers**

- waypoints now have a modifiers attribute which will indicate various temporary
  states of the waypoint
- we are going to try to move any traits that should be temporary into this
  modifiers attribute, and keep traits as permanent attributes of the waypoint
- two of these modifiers include "critical limit" and
  "unstable" for asteroids, which will be used to indiciate when an asteroid is
  being over-extracted

**Ship Fuel**

- fuel stations have been added as a waypoint type to help bridge some distances within a system
- fuel is going to become more scarce and require players to distribute supply across the system in order to maintain profitable routes
- we should have a new fuel refining ship type available to refine hydrocarbon into fuel, which should be the most profitable way to maintain fuel supplies

**Jumping Vs Warping**

- breaking change: jump drives have been removed from the game for now and players will have to use either jump gates or warp drives to travel between systems
- jump gates are now the only way to instantly travel large distances in the universe
- warp drives will allow players to travel to any system but will be quite a bit slower

**Jump Gates**

- breaking change: jump gates are no longer connected to all other jump gates within a configured range (previously it was 2500)
- each jump gate is now connected to a number of other jump gates, which means you will need to be more creative when trying to find jump gate routes across the sector
- your starting system jump gate should always be connected to the faction headquarters, where you can find some of the better ships
- every jump gate has an anti-matter exchange, and when a ship jumps, it will purchase + consume one unit of anti-matter.
- jump gates you use often will likely need to be re-supplied with anti-matter over time or the prices will skyrocket.

**Factions**

- factions are now seeded more naturally in the sector instead of evenly distributed in a grid
- some of the outer system factions may not yet be in the game for v2.1 but will be coming shortly after

**Waypoint Construction**

- waypoints can now be under construction and require delivering materials to the waypoint to complete it
- jump gates are the first waypoint type that will be under construction - you will not be able to jump across systems until the gate is complete

**Websockets**

- we are experimenting with websocket support for streaming some game data, such as ship departures and market transactions.
- this may require you to have a ship with specified mounts or modules, but allows you to see other player activity in the game in real time
- we are not sure yet how websockets will be documented, but they will use the
  same data types as our other endpoints

---

## September 30, 2023

No updates this week as we continue to work on some larger changes with
v2.1 where we are re-working the starting systems, adding multiple asteroids to
replace asteroid fields, changing jump gates so they are connected to other
jump gates, and adding some new ship types and trade goods.

This release will also be a two week cycle as we won't be available next weekend
to reset the server. We will likely have v2.1 ready for the following week if
all goes well.

---

## September 23, 2023

This week we've updated the shape of the galaxy to a three-armed spiral
galaxy, and a few small bug fixes.

**Updates**

- new galaxy shape (3-armed spiral)

**Fixes**

- extract/survey endpoint should now actually use the survey
- added shipCount to my/agent endpoint

We are also continuing to work on a few new game mechanics along with a brand new
starting system seeder which will come out in a future release. Some of these new mechanics coming up will
include:

- random starting locations for each agent that joins a faction
- seeding dozens of individual asteroids, each with potentially richer deposits
  of ores and metals
- limits to the rate at which you can mine an asteroid before it becomes
  "unstable"
- related to the above, waypoints will now have "modifiers" for different states
  of the waypoint, such as "unstable" or "stripped" (for asteroids), and others
  for markets and shipyards
- ships will now become locked in "engagements" during certain activities, such as
  surveying or generating contracts
- re-working the jump gate network so jump gates have direct connections to
  other jump gates
- some new ship types and trade goods

We will probably tag these upcoming changes as our "v2.1" release, and will
anounce when we are ready to release them.

---

## September 14, 2023

Hello everyone! We are back from summer break and diving back in to regular
updates. This week we fixed a few reported issues. Note that there is a
deprecated property on ShipNavRoute and a new endpoint for extracting with
surveys that you will want to update before the next reset.

In the next few weeks we may be updating the seeder to change the starting
conditions for new agents, which will likely invalidate some of your existing
trading strategies that rely on your starter system dynamics. With change comes
new opoprtunities to make it to the leaderboard!

**Updates**

- the Ship schema will now include a `cooldown` so players no longer need to hit
  a separate endpoint to get the cooldown status. In the instance where a ship
  has no cooldown, the expiration key will be undefined and seconds remaining
  will be 0.
- import market trade volume will now only grow when related exports are being
  fulfilled. There may also be tweaks to how often this occurs. We will continue
  to update market growth and contraction over the next few weeks to simulate
  interesting opportunities for players to take advantage of.
- the ShipNavigation schema now has an `origin` property to replace the
  `departure` property. The `departure` key is going to be re-purposed as a timestamp, so
  `arrival: Date` and `departure: Date` will be aligned, and `origin` and
  `destination` will detail the waypoints of the ship's navigation.
- players can now see the modification fee for installing and removing mounts.
  This fee is charged per mount install / removal. When module modifications are
  added, this fee will be charged per slot of the module.
- a new endpoint has been added to make extractions with surveys more explicit,
  and we will be deprecating the `survey` property on the current extract
  endpoint. You will want to migrate your survey extractions to the new
  `/my/ships/{shipSymbol}/extract/survey` endpoint.
- adds a new property `orbits` to Waypoint which is the parent symbol if the
  waypoint is orbiting another waypoint, otherwise this property is undefined.
- adds a `crew` property to ShipyardShip to detail the crew `required` and
  `capacity` fields for the ship type.

**Deprecations**

- ShipNavigation property `departure` is now deprecated in favor of `origin`.
  Next week we will re-purpose the `departure` property to replace
  `departureTime` so `arrival` and `departure` will be aligned as timestamps,
  and `origin` and `destination` will detail the ship's navigation waypoints.
- the `survey` property on the extraction endpoint is now deprecated in favor of the
  separate endpoint `/my/ships/{shipSymbol}/extract/survey`. This will allow us
  to better communicate survey related errors to the user.

**New Endpoints**

- `/my/ships/{shipSymbol}/extract/survey`

**Internal**

- updated our database client library to the latest major version

---

## June 24, 2023

This week is just a light release of bug fixes and minor updates. We will have
to skip a reset next weekend due to our schedules, but we'll be back the
following week with a new release.

The only major change this week is downgrading diamond profitability to be
closer to gold and platinum (sorry diamond miners!). There will be two weeks
between resets, so maybe the downgrade in diamond prices will stretch things out
a bit.

We've downgraded some of the extra server resources to optimize costs. There is
a small chance we are too close to the limit, which might require some downtime
mid-week to add resources back in.

**Updates**

- An agent symbol that's already taken now throws a 409 error instead of 422 (013037d4)
- Diamonds are now as profitable as gold or platinum (a78b9722)
- Contracts now increase the supply at the market on fulfillment (0b91098a)
- Increased the credits leaderboard to 15 spots (9ad38718)

**Fixes**

- Fixed bug in the refine response fields for trade symbol (af99736c)
- Added diamonds to Surveyor III (54a7adbd)
- Fixed 500 bug with surveying waypoints without traits (ce73b2de)
- Fixed bug with refuel amounts not being accurate (11da3508)

---

## June 17, 2023

This week we mostly focused on some bug fixes and server maintanence tasks
that we've been putting off for a while.

Going into our summer schedule, updates might be a bit slower than usual
depending on vacation schedules, but we'll still be around to fix bugs and
answer questions. We might take the time to work on some larger features that
require more time to implement. However we'll continue to maintain regular
weekly resets while the economy is hot.

Next week we may experiment with extending some of the travel times to make the
economy remain balanced longer into the week. As always, if you find any bugs or
discover any exploits, please let us know!

**Breaking**

- Corrected the transaction object in the install / remove 201 response (5ae4f737)

**Updates**

- Slightly nerfed surveys to have fewer yields and occurrences (c0e04734)
- Provided more cargo modules on heavy freighters (1f8fbdcb)
- Added an option to specify the refuel amount in the refuel request (69f2d40a)
- Increased the system count to 12k (be5a3a72)

**Fixes**

- Fixed the ship role on the probe ship (0a14c9e8)
- Resolved a server error on extraction (bb56cf52)
- Corrected the sell cargo error message (2d985d3f)
- Orbital stations are now correctly marked as orbitals to a parent waypoint (d8785a01)
- Improved universe seeding: starter waypoints are now closer together, and
- starter systems are seeded with closer waypoints for fuel (ad4c2f0b, 2bc6e377)

---

## June 10, 2023

This week was busier for the team so we didn't have a chance to add any new game mechanics, but we did fix a few bugs and tweak some of the game mechanics from last week's release.

In this release, we've implemented several game mechanics updates to improve gameplay experience and balance the universe economy. Notably, warping is now slower than inner-system travel, and exchange purchase/sell prices are more aligned with lower margins across the universe. In addition, new requirements for navigation and adjustments to mining and trade have been introduced to enrich the universe's economy. In response to player feedback and our ongoing testing, we've also resolved several bugs and improved system performance.

**Breaking**

- Navigation and warp now require the ship to be in orbit (70f88b05)

**Updates**

- Changed travel mechanics: warping is now slower than inner-system travel (8a258ac0)
- Rebalanced economy: exchange purchase/sell prices are more aligned, margins are a bit lower across the universe, starter system exchanges now support higher volumes in common ores and minerals, and - have lower trade volume for diamonds (729b29f5, def78e67)
- Mining lasers now only extract ores and metals; mineral deposits now contain precious stones (def78e67)
- Preparing to add gas extraction and fuel refinement (bb274b58)

**Fixes**

- Corrected negotiate contract status from 200 to 201 (fba6e0bd)
- Fixed bug allowing installation of one more mount than specs allow (2b7ead08)
- Fixed game description of mineral deposits (bd9f318c)
- Validated mount symbol on install (7afd2537)

Enjoy your updated journey across the universe!

---

## June 03, 2023

This week's reset focused on tweaking the starter system economics and removing some exploits from last week's release. We also added the ability to install and remove mounts from your ships using the new `/my/ships/{shipSymbol}/mounts` endpoints.

There is only one breaking change this week that will likely affect your scripts. Purchasing a ship will now require a ship to be present at the location of the shipyard. This is to prevent agents from too easily spreading across the galaxy.

To continue to make the quickstart as easy as possible, a probe ship is seeded at your starting shipyard to enable ship purchasing right away.

We also applied various tweaks to starter systems markets and asteroids:

- the starting system asteroid now only contains common metal deposits, meaning agents will need to venture outside of the starting system to maximize profits from mining.
- exchange prices should now better incentivize agents to sell when supplies are low, and purchase when supplies are high
- trade volume has been lowered across the starting system meaning agents are likely to see more volatile prices early on in the reset
- market growth / decay is being tested this reset, so players should see trade volume increase with consistent trade and when imports are met (and thus more stable prices)
- exchanges have been seeded at asteroids in populated systems across the galaxy
- starting contracts are now much easier to complete due to the smaller trade volumes and various bugs have been fixed
- contract deliveries should now come from the least supplied markets and the new agent contract should provide better "on-fulfilled" payment terms
- to compensate for lower contract payments, starting agents will begin with 150,000 credits
- contracts should start expiring this week and will be removed if you don't accept the terms; generating new contracts are still a WIP so if you find bugs please let us know

Later during this reset we might be adding the ability to install / remove modules as well, but it might wait until the following week. We had a busy weekend with the holiday so there is still a lot of work to do that didn't make it into this reset.

Enjoy and please file bugs and exploits as you explore!

**Breaking**

- Added requirement of ship presence at shipyard for purchasing a ship (6c4e3fe9)

**Updates**

- Added ability to install and remove ship mounts (05d1248c)
- Enhanced new agent experience: easier new agent contracts, increased new agent contract payment, new agent probe ship at shipyard (13f7629f, 14695b27, 64a9b892)
- Updated trade and economy: rebalanced trade prices, tweaked price of fuel, removed antimatter from starting systems and homeworld exports (fbcf99da, 1ed2f29c, e95caf99)
- Changed starter system parameters (b82e5695)

**Fixes**

- Fixed various contract-related bugs: bug with contract generation selecting over supplied markets, bug with contract generation, contract delivery at wrong destination, new agent contract destination (f637766f, 73379e77, 02091bba, 43fccb03)
- Addressed a bug with charting waypoints (d838011b)
- Improved data in ShipInTransitError (303c17c7)

**Internal**

- Updated background jobs for contract processing and market growth (63a03f4e, 6d8ac036, 39b8b201 fab37233, 3640c6b2, 4079ca6a)
- Added module install command, ship install / remove error codes, and refactored register agent (6df4b927, 3adb05e0, 94ff962b, 751955d4)

**Documentation**

- Updated quickstart guide with new probe (8dbbb5d4)

---

## May 20, 2023

In this release, we continued to apply fixes and tweak gameplay mechanics. The universe seeder parameters have been updated to offer more factions, more shipyards and more markets. We've also added the ability to generate contracts, which we will further enhance in the next release. Contracts can now expire and the faction will take back any credits advanced to the agent. Agents can only have one contract at a time until we have a chance to add more features around negotiation.

Next week we will either need to reset on Friday or the following Monday, or skip a week due to scheduling conflicts with the holiday weekend. We will announce the decision in the `#announcements` channel on Discord.

**Breaking**

- fixed Retry-After header to conform to whole seconds
- ships can no longer extract while docked
- Cooldown expiredAt is now an optional field (preparing to convert the cooldown response from 204 to 200)
- Contract field `expiration` has been deprecated in favor of `deadlineToAccept`

**Updates**

- Tweaked universe seeding parameters and contract generation parameters (b028d92f, 898abbbc)
- Enhanced faction dynamics: added faction flag for recruitment status and starting faction field to agent (6b71144a, b6927b45)
- Updated transaction elements: added transaction to refuel response, increased transaction history to 20 items (dc6f5a2c, dc7501f2)
- Adjusted game mechanics: increased scarcity of diamonds, lowered jump gate range with cooldown as a product of distance jumped, added negotiate contract endpoints, and fixed starting contract params, added contract expiry and advance credits repossession (b1ecf871, 6465bf59, e1f839cd, 3d30b3f3)
- Enhanced agent token with version and reset_date (a0c3344a)
- Updated status endpoint to include more info, reset, and links (f30290f2, 5fc47f70, 37177c17)
- Contracts can now fail and the faction will reclaim any advance credits provided on accepting the contract
- New experimental `/my/agent/events` endpoint which should show you the last 60 seconds of events that have happened to your agent (right now this is just where failed contracts will be recorded)

**Fixes**

- Addressed various gameplay bugs: fixed ship transfer rules, , addressed issues with chartable systems, survey validation date time format, and survey exhausted error, and fixed refining and extraction while on cooldown bugs (b609eb9c, f11a9e45, edc87ede, ac820dd7, 35bff480, cc4a5eb2, 7d43f3d0)
- Adjusted agent symbol check in transaction and made integer only in pagination (4cb08b63, ee0b9c6c)
- Ensured ship must be in orbit to extract (36f4e0ff)

**Internal**

- Provided a helpful message for error regarding reserved call signs (4e6753da)
- Regenerated OpenAPI types (f123a3c1, e1f839cd)
- Added server resets page to docs and fixed tests (d5744a19, 79af1229)
- Optimized several endpoints including contract deliver, warp, ship transfer, refuel, navigate route, dock and orbit routes, sell cargo, and extraction (5dcef3f9, bb0499d4, faca4373, d545f0b7, e6e89f06, fe19bbb5, af8be35f, 7ebbfacb, 77781131)
- Updated language in changelog, added more test commands, and increased volume for refinement of goods (c08250db, d1c31fe3, c3d24fd8)
- Added changelog page (20646299)

**Documentation**

- Updated rate limit page with DDoS information (2580e38f)

We'll be discussing what to focus on for the next reset in Discord (likely installing / removing modules and mounts). Enjoy!

---

## May 14, 2023

This week we focused primarily on bug fixes and internal improvements. We also added the ability to reserve call signs with Stripe donations.

The server was reset on May 13, 2023 at 10:00AM PST. All tokens prior to the reset are now invalid. You will need to register a new agent and generate a new access token to play the game.

We will be resetting the server on a regular cadence until we are confident that the game is stable enough to run for longer periods of time.

This will be announced in the `#announcements` channel on Discord. We will also add data to the status endpoint to indicate when the next reset will occur, and better handle error messages when users attempt to use an invalid token.

Next week we will continue to focus on patching core issues, improving documentation, and solidfying the process around server resets and how we communicate them.

**Fixes**

- fixed exploit with refining while on cooldown
- fixed exploit with extraction while on cooldown
- fixed bug where a cooldown would still happen even when an error is thrown
- fixed the server error message to link to the new api-docs repository
- fixed bug where survey error was thrown after extraction
- fixed bug where shipyard supply was not updating on purchase
- fixed bug where warp drives / mineral processors were not required to warp / extract
- fixed bug where refueling ship in small quantities was free
- fixed bug where import re-purchase prices were too low during supply shock\

**Updates**

- added the ability to reserve call signs with Stripe donations

**Internals**

- fixed server 500 errors related to database connection issues
- scaled database to allow for more concurrent connections

**Removals**

- removed token validation from public endpoints

**Documentation**

- added detail about generating Open API clients from the Stoplight bundled export
- fixed various typos and links
- added clarification on how refueling works
- added clarification on how sector / system / waypoint symbols work
- added donation link to support the game
