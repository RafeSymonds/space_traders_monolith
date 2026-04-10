from dataclasses import dataclass
from datetime import datetime

from app.core.fleet_manager import FleetManager, ShipRole, TrackedShip
from space_traders_api import FleetApi, SystemsApi


@dataclass
class SystemScanResult:
    ship_symbol: str
    system: str
    waypoints_found: int
    factions_found: int
    timestamp: datetime


@dataclass
class WaypointScanResult:
    ship_symbol: str
    waypoint: str
    traits: list[str]
    modifiers: list[str]
    timestamp: datetime


@dataclass
class ChartResult:
    ship_symbol: str
    waypoint: str
    submitted_by: str
    timestamp: datetime


class ExplorationBot:
    def __init__(
        self,
        fleet_api: FleetApi,
        systems_api: SystemsApi,
        fleet_manager: FleetManager,
    ):
        self._fleet = fleet_api
        self._systems = systems_api
        self._fleet_manager = fleet_manager

    def scan_system(
        self,
        ship: TrackedShip,
        system_symbol: str,
    ) -> SystemScanResult:
        ship.is_busy = True
        ship.last_action = f"scanning system {system_symbol}"

        try:
            result = self._fleet.create_ship_system_scan(
                ship_symbol=ship.symbol,
            )

            waypoints = 0
            factions = 0

            if result.data and result.data.scan:
                waypoints = len(result.data.scan.waypoints) if result.data.scan.waypoints else 0
                factions = len(result.data.scan.factions) if result.data.scan.factions else 0

            return SystemScanResult(
                ship_symbol=ship.symbol,
                system=system_symbol,
                waypoints_found=waypoints,
                factions_found=factions,
                timestamp=datetime.now(),
            )

        finally:
            ship.is_busy = False

    def scan_waypoints(
        self,
        ship: TrackedShip,
    ) -> list[WaypointScanResult]:
        ship.is_busy = True
        ship.last_action = "scanning waypoints"

        try:
            result = self._fleet.create_ship_waypoint_scan(
                ship_symbol=ship.symbol,
            )

            scans = []
            if result.data and result.data.scan:
                for wp in result.data.scan.waypoints:
                    traits = (
                        [t.symbol.value if hasattr(t.symbol, "value") else str(t.symbol) for t in wp.traits]
                        if wp.traits
                        else []
                    )
                    modifiers = (
                        [m.symbol.value if hasattr(m.symbol, "value") else str(m.symbol) for m in wp.modifiers]
                        if wp.modifiers
                        else []
                    )

                    scans.append(
                        WaypointScanResult(
                            ship_symbol=ship.symbol,
                            waypoint=wp.symbol,
                            traits=traits,
                            modifiers=modifiers,
                            timestamp=datetime.now(),
                        ),
                    )

            return scans

        finally:
            ship.is_busy = False

    def chart_waypoint(
        self,
        ship: TrackedShip,
        waypoint: str,
    ) -> ChartResult:
        ship.is_busy = True
        ship.last_action = f"charting {waypoint}"

        try:
            result = self._fleet.create_chart(
                ship_symbol=ship.symbol,
            )

            chart = result.data.chart if result.data else None

            return ChartResult(
                ship_symbol=ship.symbol,
                waypoint=waypoint,
                submitted_by=chart.submitted_by if chart else "unknown",
                timestamp=datetime.now(),
            )

        finally:
            ship.is_busy = False

    def jump_to_system(
        self,
        ship: TrackedShip,
        system_symbol: str,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = f"jumping to {system_symbol}"

        try:
            result = self._fleet.jump_ship(
                ship_symbol=ship.symbol,
                jump_ship_request={"system_symbol": system_symbol},
            )

            return {
                "success": True,
                "ship": ship.symbol,
                "destination": system_symbol,
            }

        finally:
            ship.is_busy = False

    def warp_to_waypoint(
        self,
        ship: TrackedShip,
        waypoint_symbol: str,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = f"warping to {waypoint_symbol}"

        try:
            result = self._fleet.warp_ship(
                ship_symbol=ship.symbol,
                warp_ship_request={"waypoint_symbol": waypoint_symbol},
            )

            return {
                "success": True,
                "ship": ship.symbol,
                "destination": waypoint_symbol,
            }

        finally:
            ship.is_busy = False

    def explore_system(
        self,
        ship: TrackedShip,
        system_symbol: str,
    ) -> dict:
        results = {
            "system_scan": None,
            "waypoint_scans": [],
            "charts": [],
        }

        scan_result = self.scan_system(ship, system_symbol)
        results["system_scan"] = {
            "waypoints_found": scan_result.waypoints_found,
            "factions_found": scan_result.factions_found,
        }

        waypoint_scans = self.scan_waypoints(ship)
        results["waypoint_scans"] = [
            {
                "waypoint": w.waypoint,
                "traits": w.traits,
                "modifiers": w.modifiers,
            }
            for w in waypoint_scans
        ]

        return results


class FleetCoordinator:
    def __init__(
        self,
        fleet_api: FleetApi,
        fleet_manager: FleetManager,
    ):
        self._fleet = fleet_api
        self._fleet_manager = fleet_manager
        self._missions: list[dict] = []

    def assign_role(
        self,
        ship_symbol: str,
        role: ShipRole,
    ) -> dict:
        ship = self._fleet_manager.get_ship(ship_symbol)
        if not ship:
            return {"success": False, "error": "Ship not found"}

        ship.role = role
        return {"success": True, "ship": ship_symbol, "role": role.value}

    def get_ships_by_role(self, role: ShipRole) -> list[TrackedShip]:
        return self._fleet_manager.get_ships_by_role(role)

    def get_available_ships(
        self,
        role: ShipRole | None = None,
    ) -> list[TrackedShip]:
        return self._fleet_manager.get_available_ships(role)

    def create_mining_fleet(
        self,
        num_miners: int = 3,
    ) -> dict:
        available = self.get_available_ships(ShipRole.MINING)
        if len(available) < num_miners:
            available = self.get_available_ships()

        miners = available[:num_miners]
        for miner in miners:
            self.assign_role(miner.symbol, ShipRole.MINING)

        return {
            "success": True,
            "miners": [m.symbol for m in miners],
        }

    def create_trading_fleet(
        self,
        num_traders: int = 2,
    ) -> dict:
        available = self.get_available_ships(ShipRole.TRADING)
        if len(available) < num_traders:
            available = self.get_available_ships()

        traders = available[:num_traders]
        for trader in traders:
            self.assign_role(trader.symbol, ShipRole.TRADING)

        return {
            "success": True,
            "traders": [t.symbol for t in traders],
        }

    def coordinate_trade_run(
        self,
        cargo_ship_symbol: str,
        mining_ships: list[str],
        buy_waypoint: str,
        sell_waypoint: str,
    ) -> dict:
        cargo_ship = self._fleet_manager.get_ship(cargo_ship_symbol)
        if not cargo_ship:
            return {"success": False, "error": "Cargo ship not found"}

        cargo_available = cargo_ship.cargo_available

        results = {
            "cargo_loaded": 0,
            "trades_executed": 0,
            "errors": [],
        }

        for miner_symbol in mining_ships:
            miner = self._fleet_manager.get_ship(miner_symbol)
            if not miner or miner.cargo_used == 0:
                continue

            cargo_to_transfer = min(miner.cargo_used, cargo_available)

            try:
                self._fleet.transfer_cargo(
                    ship_symbol=miner.symbol,
                    transfer_cargo_request={
                        "ship_symbol": cargo_ship_symbol,
                        "units": cargo_to_transfer,
                    },
                )
                results["cargo_loaded"] += cargo_to_transfer
            except Exception as e:
                results["errors"].append(f"Transfer from {miner_symbol}: {e!s}")

        return results
