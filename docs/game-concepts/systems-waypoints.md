<!-- Mirrored from https://docs.spacetraders.io/game-concepts/systems-waypoints -->

# Systems and Waypoints

## Overview

The SpaceTraders universe is made of up of systems and waypoints. Every system has a type, which is typically a type of star, and a set of x, y coordinates.

Waypoints are locations within a system that you can travel to. They can be planets, asteroids fields, orbital stations, or any other type of location.

Ships can navigate between waypoints and jump or warp between systems.

## Systems

Systems are the primary locations in the SpaceTraders universe. There are roughly 8,500 systems, and 200k waypoints in the universe to explore. You can view a list of all systems in the universe by calling the following endpoint:

```bash
curl -X GET 'https://api.spacetraders.io/v2/systems'
```

The best way to visualize the universe would be to plot the x and y coordinates of each system on a graph, which should show a rough spiral shape for the universe.

Although a majority of system types are stars, there are also a few other types of systems. Some of these include Black Holes, Neutron Stars, and Nebula.

**Future**: Be careful when traveling into unknown systems, as some of these types can be dangerous to your ships.

## Waypoints

Waypoints are locations within a system that you can travel to. They can be planets, asteroids fields, orbital stations, or any other type of traversable location with an x, y coordinate.

You can view a list of all waypoints in a system by calling the following endpoint:

```bash
curl -X GET 'https://api.spacetraders.io/v2/systems/:systemSymbol/waypoints'
```

A waypoint has a type, a set of x, y coordinates, and a unique symbol name that you can use to reference it. Waypoints may also have orbital waypoints, which are locations within the orbit of the location.

Orbitals are other waypoints that are located at the exact same x, y coordinates as that waypoint. They'll have an parentSymbol property to indicate what they are in orbit of.

For example, a planet may have an space station as well as two moons that orbit it. The planet itself would be the parent waypoint, and the space station and moons would be orbital waypoints.

When visualizing a system, you can map the coordinates of each waypoint to a graph to see where they are located in the system.

### Traits

Waypoints have a list of traits that describe the details, features and characteristics of the location. For example, a planet may have a trait that describes the atmosphere as "toxic", the political leanings as "authoritarian", or the population as "sparse"

Two traits that are particularly important are the `MARKETPLACE` and `SHIPYARD` traits. These traits indicate that the location has a marketplace and shipyard, respectively. You can use these traits to determine if you can buy or sell goods at a location, or if you can purchase a new ship.

### Modifiers

Waypoint can also have modifiers. These are temporary effects that apply to a waypoint. The distiction between traits and modifiers is that the modifiers come and go, and traits are static over the duration of a reset.

Currently the only modifiers with any effect is the critical limit modifier, which applies to asteroid waypoints if they're at risk of being overextracted.
