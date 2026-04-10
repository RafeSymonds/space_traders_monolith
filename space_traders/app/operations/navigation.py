from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from space_traders_api import FleetApi, SystemsApi


class JumpGateConnection:
    def __init__(self, destination: str, distance: int, fuel_cost: int):
        self.destination = destination
        self.distance = distance
        self.fuel_cost = fuel_cost


@dataclass
class ConstructionSite:
    waypoint_symbol: str
    system_symbol: str
    materials_needed: list[dict]
    materials_filled: list[dict]
    is_complete: bool
    estimate_completion: str | None
    progress_percent: float


@dataclass
class NavigationResult:
    success: bool
    ship_symbol: str
    destination: str
    fuel_consumed: int
    duration_seconds: int
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class JumpGateNavigator:
    def __init__(self, fleet_api: FleetApi, systems_api: SystemsApi):
        self._fleet = fleet_api
        self._systems = systems_api
        self._jump_gate_cache: dict[str, list[JumpGateConnection]] = {}
        self._navigation_history: list[NavigationResult] = []

    def get_jump_gate_connections(
        self,
        system_symbol: str,
        waypoint_symbol: str,
    ) -> list[JumpGateConnection]:
        cache_key = f"{system_symbol}:{waypoint_symbol}"
        if cache_key in self._jump_gate_cache:
            return self._jump_gate_cache[cache_key]

        try:
            result = self._systems.get_jump_gate(
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
            )

            connections = []
            if result.data and hasattr(result.data, "connections"):
                for conn in result.data.connections:
                    connections.append(
                        JumpGateConnection(
                            destination=getattr(conn, "symbol", "UNKNOWN"),
                            distance=getattr(conn, "distance", 0) or 0,
                            fuel_cost=getattr(conn, "fuel_cost", 0) or 0,
                        ),
                    )

            self._jump_gate_cache[cache_key] = connections
            return connections

        except Exception:
            return []

    def jump_ship(
        self,
        ship_symbol: str,
        destination_system: str,
    ) -> NavigationResult:
        try:
            result = self._fleet.jump_ship(
                ship_symbol=ship_symbol,
                jump_ship_request={"system_symbol": destination_system},
            )

            fuel_consumed = 0
            duration = 0

            if result.data and result.data.nav:
                fuel_consumed = getattr(result.data.nav, "fuel_consumed", 0) or 0
                route = result.data.nav.route if hasattr(result.data.nav, "route") else None
                if route:
                    departure = getattr(route, "departure_time", None)
                    arrival = getattr(route, "arrival", None)
                    if departure and arrival:
                        duration = int((arrival - departure).total_seconds())

            nav_result = NavigationResult(
                success=True,
                ship_symbol=ship_symbol,
                destination=destination_system,
                fuel_consumed=fuel_consumed,
                duration_seconds=duration,
            )

            self._navigation_history.append(nav_result)
            return nav_result

        except Exception as e:
            return NavigationResult(
                success=False,
                ship_symbol=ship_symbol,
                destination=destination_system,
                fuel_consumed=0,
                duration_seconds=0,
                error=str(e),
            )

    def warp_ship(
        self,
        ship_symbol: str,
        destination_waypoint: str,
    ) -> NavigationResult:
        try:
            result = self._fleet.warp_ship(
                ship_symbol=ship_symbol,
                warp_ship_request={"waypoint_symbol": destination_waypoint},
            )

            fuel_consumed = 0
            duration = 0

            if result.data and result.data.nav:
                fuel_consumed = getattr(result.data.nav, "fuel_consumed", 0) or 0
                route = result.data.nav.route if hasattr(result.data.nav, "route") else None
                if route:
                    departure = getattr(route, "departure_time", None)
                    arrival = getattr(route, "arrival", None)
                    if departure and arrival:
                        duration = int((arrival - departure).total_seconds())

            nav_result = NavigationResult(
                success=True,
                ship_symbol=ship_symbol,
                destination=destination_waypoint,
                fuel_consumed=fuel_consumed,
                duration_seconds=duration,
            )

            self._navigation_history.append(nav_result)
            return nav_result

        except Exception as e:
            return NavigationResult(
                success=False,
                ship_symbol=ship_symbol,
                destination=destination_waypoint,
                fuel_consumed=0,
                duration_seconds=0,
                error=str(e),
            )

    def navigate_ship(
        self,
        ship_symbol: str,
        destination_waypoint: str,
    ) -> NavigationResult:
        try:
            result = self._fleet.navigate_ship(
                ship_symbol=ship_symbol,
                navigate_ship_request={"waypoint_symbol": destination_waypoint},
            )

            fuel_consumed = 0
            duration = 0

            if result.data and result.data.nav:
                fuel_consumed = getattr(result.data.nav, "fuel_consumed", 0) or 0
                route = result.data.nav.route if hasattr(result.data.nav, "route") else None
                if route:
                    departure = getattr(route, "departure_time", None)
                    arrival = getattr(route, "arrival", None)
                    if departure and arrival:
                        duration = int((arrival - departure).total_seconds())

            nav_result = NavigationResult(
                success=True,
                ship_symbol=ship_symbol,
                destination=destination_waypoint,
                fuel_consumed=fuel_consumed,
                duration_seconds=duration,
            )

            self._navigation_history.append(nav_result)
            return nav_result

        except Exception as e:
            return NavigationResult(
                success=False,
                ship_symbol=ship_symbol,
                destination=destination_waypoint,
                fuel_consumed=0,
                duration_seconds=0,
                error=str(e),
            )

    def get_flight_mode(self, ship_symbol: str) -> str | None:
        try:
            result = self._fleet.get_ship_nav(ship_symbol=ship_symbol)
            if result.data:
                return getattr(result.data, "flight_mode", "CRUISE")
        except Exception:
            pass
        return None

    def set_flight_mode(self, ship_symbol: str, mode: str) -> dict:
        valid_modes = ["CRUISE", "DRIFT", "BURN", "STEALTH"]
        if mode not in valid_modes:
            return {"success": False, "error": f"Invalid mode. Must be one of {valid_modes}"}

        try:
            result = self._fleet.update_ship_nav(
                ship_symbol=ship_symbol,
                update_ship_nav_request={"flight_mode": mode},
            )

            if result.data:
                return {"success": True, "ship": ship_symbol, "mode": mode}

            return {"success": False, "ship": ship_symbol, "error": "No data returned"}

        except Exception as e:
            return {"success": False, "ship": ship_symbol, "error": str(e)}

    def get_navigation_history(self, limit: int = 50) -> list[dict]:
        history = []
        for result in self._navigation_history[-limit:]:
            history.append(
                {
                    "success": result.success,
                    "ship": result.ship_symbol,
                    "destination": result.destination,
                    "fuel_consumed": result.fuel_consumed,
                    "duration_seconds": result.duration_seconds,
                    "error": result.error,
                    "timestamp": result.timestamp.isoformat(),
                },
            )
        return history

    def get_stats(self) -> dict:
        total_jumps = len(self._navigation_history)
        successful = sum(1 for r in self._navigation_history if r.success)
        total_fuel = sum(r.fuel_consumed for r in self._navigation_history if r.success)

        return {
            "total_navigations": total_jumps,
            "successful": successful,
            "failed": total_jumps - successful,
            "total_fuel_consumed": total_fuel,
        }


class ConstructionManager:
    def __init__(self, fleet_api: FleetApi, systems_api: SystemsApi):
        self._fleet = fleet_api
        self._systems = systems_api
        self._construction_history: list[dict] = []

    def get_construction_site(
        self,
        system_symbol: str,
        waypoint_symbol: str,
    ) -> ConstructionSite | None:
        try:
            result = self._systems.get_construction(
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
            )

            if not result.data:
                return None

            data = result.data

            materials_needed = []
            materials_filled = []

            if hasattr(data, "materials") and data.materials:
                for mat in data.materials:
                    materials_needed.append(
                        {
                            "symbol": getattr(mat, "symbol", "UNKNOWN"),
                            "units_required": getattr(mat, "required", 0) or 0,
                        },
                    )
                    materials_filled.append(
                        {
                            "symbol": getattr(mat, "symbol", "UNKNOWN"),
                            "units_filled": getattr(mat, "fulfilled", 0) or 0,
                        },
                    )

            is_complete = getattr(data, "is_complete", False)
            progress = 0
            if materials_needed and materials_filled:
                total_required = sum(m["units_required"] for m in materials_needed)
                total_filled = sum(m["units_filled"] for m in materials_filled)
                progress = (total_filled / total_required * 100) if total_required > 0 else 0

            return ConstructionSite(
                waypoint_symbol=waypoint_symbol,
                system_symbol=system_symbol,
                materials_needed=materials_needed,
                materials_filled=materials_filled,
                is_complete=is_complete,
                estimate_completion=getattr(data, "estimated_time_remaining", None),
                progress_percent=progress,
            )

        except Exception:
            return None

    def supply_construction(
        self,
        ship_symbol: str,
        waypoint_symbol: str,
        trade_symbol: str,
        units: int,
    ) -> dict:
        try:
            result = self._fleet.supply_construction(
                ship_symbol=ship_symbol,
                waypoint_symbol=waypoint_symbol,
                supply_construction_request={
                    "symbol": trade_symbol,
                    "units": units,
                },
            )

            if result.data:
                self._construction_history.append(
                    {
                        "ship": ship_symbol,
                        "waypoint": waypoint_symbol,
                        "material": trade_symbol,
                        "units": units,
                        "success": True,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                return {
                    "success": True,
                    "ship": ship_symbol,
                    "waypoint": waypoint_symbol,
                    "material": trade_symbol,
                    "units": units,
                }

            return {"success": False, "ship": ship_symbol, "error": "No data returned"}

        except Exception as e:
            return {"success": False, "ship": ship_symbol, "error": str(e)}

    def find_construction_sites(
        self,
        system_symbol: str,
        waypoints: list[str],
    ) -> list[ConstructionSite]:
        sites = []
        for waypoint in waypoints:
            site = self.get_construction_site(system_symbol, waypoint)
            if site:
                sites.append(site)
        return sites

    def get_history(self) -> list[dict]:
        return self._construction_history
