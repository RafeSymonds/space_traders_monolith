from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from space_traders_api import ContractsApi, FleetApi


class ContractState(Enum):
    IDLE = "idle"
    ACCEPTING = "accepting"
    ACCEPTED = "accepted"
    FULFILLING = "fulfilling"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ContractDelivery:
    trade_symbol: str
    units_required: int
    units_fulfilled: int
    units_needed: int


@dataclass
class TrackedContract:
    id: str
    faction: str
    contract_type: str
    payment_on_accepted: int
    payment_on_fulfilled: int
    deadline: datetime
    deliveries: list[ContractDelivery]
    state: ContractState
    accepted: bool
    fulfilled: bool
    accepted_at: datetime | None = None
    fulfilled_at: datetime | None = None


@dataclass
class ContractResult:
    success: bool
    contract_id: str
    action: str
    details: dict = field(default_factory=dict)
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class ContractAutomation:
    def __init__(self, contracts_api: ContractsApi, fleet_api: FleetApi):
        self._contracts = contracts_api
        self._fleet = fleet_api
        self._tracked: list[TrackedContract] = []
        self._action_history: list[ContractResult] = []

    def fetch_contracts(self) -> list[dict]:
        try:
            result = self._contracts.get_contracts()
            return result.data or []
        except Exception:
            return []

    def accept_contract(self, contract_id: str) -> ContractResult:
        try:
            result = self._contracts.accept_contract(contract_id=contract_id)
            if result.data and result.data.contract:
                contract = result.data.contract
                self._track_contract(contract, accepted=True)
                return ContractResult(
                    success=True,
                    contract_id=contract_id,
                    action="accepted",
                    details={"payment": contract.payment.get("onAccepted", 0) if contract.payment else 0},
                )
            return ContractResult(success=False, contract_id=contract_id, action="accepted", error="No data returned")
        except Exception as e:
            return ContractResult(success=False, contract_id=contract_id, action="accepted", error=str(e))

    def fulfill_contract(self, contract_id: str) -> ContractResult:
        try:
            result = self._contracts.fulfill_contract(contract_id=contract_id)
            self._update_tracked_state(contract_id, ContractState.COMPLETED)
            return ContractResult(
                success=True,
                contract_id=contract_id,
                action="fulfilled",
                details={
                    "payment": result.data.contract.payment.get("onFulfilled", 0)
                    if result.data and result.data.contract and result.data.contract.payment
                    else 0
                },
            )
        except Exception as e:
            return ContractResult(success=False, contract_id=contract_id, action="fulfilled", error=str(e))

    def deliver_to_contract(
        self,
        contract_id: str,
        ship_symbol: str,
        trade_symbol: str,
        units: int,
    ) -> ContractResult:
        try:
            result = self._contracts.deliver_contract(
                contract_id=contract_id,
                deliver_request={
                    "ship_symbol": ship_symbol,
                    "trade_symbol": trade_symbol,
                    "units": units,
                },
            )
            self._update_tracked_state(contract_id, ContractState.DELIVERING)
            return ContractResult(
                success=True,
                contract_id=contract_id,
                action="delivered",
                details={
                    "ship": ship_symbol,
                    "trade_symbol": trade_symbol,
                    "units": units,
                    "units_fulfilled": result.data.units_fulfilled if result.data else 0,
                },
            )
        except Exception as e:
            return ContractResult(success=False, contract_id=contract_id, action="delivered", error=str(e))

    def _track_contract(self, contract_data: Any, accepted: bool = False) -> None:
        deliveries = []
        if hasattr(contract_data, "terms") and contract_data.terms:
            for d in contract_data.terms.deliver or []:
                deliveries.append(
                    ContractDelivery(
                        trade_symbol=d.trade_symbol,
                        units_required=d.units_required or 0,
                        units_fulfilled=d.units_fulfilled or 0,
                        units_needed=(d.units_required or 0) - (d.units_fulfilled or 0),
                    ),
                )

        deadline_str = getattr(contract_data, "deadline", None)
        deadline = datetime.now() + timedelta(days=7)
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
            except Exception:
                pass

        tracked = TrackedContract(
            id=getattr(contract_data, "id", "unknown"),
            faction=getattr(contract_data, "faction_symbol", "unknown"),
            contract_type=getattr(contract_data, "type", "unknown"),
            payment_on_accepted=getattr(contract_data, "payment", {}).get("onAccepted", 0)
            if hasattr(getattr(contract_data, "payment", {}), "get")
            else 0,
            payment_on_fulfilled=getattr(contract_data, "payment", {}).get("onFulfilled", 0)
            if hasattr(getattr(contract_data, "payment", {}), "get")
            else 0,
            deadline=deadline,
            deliveries=deliveries,
            state=ContractState.ACCEPTED if accepted else ContractState.IDLE,
            accepted=accepted,
            fulfilled=getattr(contract_data, "fulfilled", False),
        )

        if accepted:
            tracked.accepted_at = datetime.now()

        self._tracked.append(tracked)

    def _update_tracked_state(self, contract_id: str, state: ContractState) -> None:
        for t in self._tracked:
            if t.id == contract_id:
                t.state = state

    def get_pending_deliveries(self) -> list[dict]:
        pending = []
        for t in self._tracked:
            if t.accepted and not t.fulfilled:
                for d in t.deliveries:
                    if d.units_needed > 0:
                        pending.append(
                            {
                                "contract_id": t.id,
                                "faction": t.faction,
                                "trade_symbol": d.trade_symbol,
                                "units_needed": d.units_needed,
                                "deadline": t.deadline.isoformat(),
                            },
                        )
        return pending

    def get_stats(self) -> dict:
        return {
            "total_tracked": len(self._tracked),
            "accepted": len([t for t in self._tracked if t.accepted]),
            "fulfilled": len([t for t in self._tracked if t.fulfilled]),
            "pending_deliveries": len(self.get_pending_deliveries()),
            "total_earned": sum(t.payment_on_fulfilled for t in self._tracked if t.fulfilled),
            "pending_earnings": sum(t.payment_on_fulfilled for t in self._tracked if t.accepted and not t.fulfilled),
        }


class ContractCoordinator:
    def __init__(self, contracts_api: ContractsApi, fleet_api: FleetApi):
        self._automation = ContractAutomation(contracts_api, fleet_api)
        self._auto_accept = True

    def sync_contracts(self) -> dict:
        raw_contracts = self._automation.fetch_contracts()
        for contract_data in raw_contracts:
            existing = next((t for t in self._automation._tracked if t.id == getattr(contract_data, "id", None)), None)
            if not existing:
                accepted = getattr(contract_data, "accepted", False)
                self._automation._track_contract(contract_data, accepted=accepted)

        return {"synced": len(raw_contracts), "tracked": len(self._automation._tracked)}

    def auto_accept_available(self) -> list[ContractResult]:
        results = []
        raw = self._automation.fetch_contracts()
        for contract_data in raw:
            if not getattr(contract_data, "accepted", False):
                result = self._automation.accept_contract(getattr(contract_data, "id", ""))
                results.append(result)
        return results

    def check_and_fulfill(self) -> list[ContractResult]:
        results = []
        for tracked in self._automation._tracked:
            if tracked.accepted and not tracked.fulfilled:
                all_delivered = all(d.units_needed <= 0 for d in tracked.deliveries)
                if all_delivered:
                    result = self._automation.fulfill_contract(tracked.id)
                    results.append(result)
        return results

    def find_cargo_for_delivery(self, trade_symbol: str, units_needed: int) -> list[dict]:
        try:
            ships_result = self._fleet.get_my_ships()
            candidates = []
            for ship in ships_result.data or []:
                if ship.cargo and ship.cargo.inventory:
                    for item in ship.cargo.inventory:
                        if item.symbol == trade_symbol and item.units >= units_needed:
                            candidates.append(
                                {
                                    "ship": ship.symbol,
                                    "units_available": item.units,
                                    "units_needed": units_needed,
                                },
                            )
            return candidates
        except Exception:
            return []

    def execute_delivery(
        self,
        contract_id: str,
        ship_symbol: str,
        trade_symbol: str,
        units: int,
    ) -> ContractResult:
        return self._automation.deliver_to_contract(contract_id, ship_symbol, trade_symbol, units)

    def get_pending_contracts(self) -> list[dict]:
        return self._automation.get_pending_deliveries()

    def get_stats(self) -> dict:
        return self._automation.get_stats()
