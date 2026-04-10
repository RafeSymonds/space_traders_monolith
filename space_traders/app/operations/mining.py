from dataclasses import dataclass
from datetime import datetime

from app.core.fleet_manager import FleetManager, TrackedShip
from space_traders_api import FleetApi
from space_traders_api.models import Survey


@dataclass
class MiningYield:
    good: str
    units: int


@dataclass
class ExtractionResult:
    ship_symbol: str
    yields: list[MiningYield]
    total_units: int
    timestamp: datetime


@dataclass
class SurveyResult:
    ship_symbol: str
    waypoint: str
    deposits: list[str]
    expiration: datetime
    size: str


class MiningBot:
    def __init__(
        self,
        fleet_api: FleetApi,
        fleet_manager: FleetManager,
        cooldown_seconds: int = 60,
    ):
        self._fleet = fleet_api
        self._fleet_manager = fleet_manager
        self._cooldown_seconds = cooldown_seconds
        self._extraction_history: list[ExtractionResult] = []

    def survey(
        self,
        ship: TrackedShip,
    ) -> list[SurveyResult]:
        ship.is_busy = True
        ship.last_action = "surveying"

        try:
            result = self._fleet.create_survey(ship_symbol=ship.symbol)

            surveys = []
            if result.data and result.data.surveys:
                for survey in result.data.surveys:
                    deposits = []
                    if survey.deposits:
                        for deposit in survey.deposits:
                            deposits.append(deposit.symbol)

                    surveys.append(
                        SurveyResult(
                            ship_symbol=ship.symbol,
                            waypoint=survey.symbol,
                            deposits=deposits,
                            expiration=survey.expiration,
                            size=survey.size.value if survey.size else "UNKNOWN",
                        ),
                    )

            return surveys

        finally:
            ship.is_busy = False

    def extract_with_survey(
        self,
        ship: TrackedShip,
        survey: Survey,
    ) -> ExtractionResult:
        ship.is_busy = True
        ship.last_action = "extracting with survey"

        try:
            result = self._fleet.extract_resources_with_survey(
                ship_symbol=ship.symbol,
                survey=survey,
            )

            yields = []
            total_units = 0

            if result.data and result.data.extraction:
                extraction_yield = result.data.extraction.var_yield
                yields.append(
                    MiningYield(
                        good=extraction_yield.symbol,
                        units=extraction_yield.units,
                    ),
                )
                total_units += extraction_yield.units

            extraction = ExtractionResult(
                ship_symbol=ship.symbol,
                yields=yields,
                total_units=total_units,
                timestamp=datetime.now(),
            )
            self._extraction_history.append(extraction)
            return extraction

        finally:
            ship.is_busy = False

    def extract(
        self,
        ship: TrackedShip,
    ) -> ExtractionResult:
        ship.is_busy = True
        ship.last_action = "extracting"

        try:
            result = self._fleet.extract_resources(ship_symbol=ship.symbol)

            yields = []
            total_units = 0

            if result.data and result.data.extraction:
                extraction_yield = result.data.extraction.var_yield
                yields.append(
                    MiningYield(
                        good=extraction_yield.symbol,
                        units=extraction_yield.units,
                    ),
                )
                total_units += extraction_yield.units

            extraction = ExtractionResult(
                ship_symbol=ship.symbol,
                yields=yields,
                total_units=total_units,
                timestamp=datetime.now(),
            )
            self._extraction_history.append(extraction)
            return extraction

        finally:
            ship.is_busy = False

    def continuous_mining(
        self,
        ship: TrackedShip,
        cycles: int = 10,
        use_surveys: bool = True,
    ) -> list[ExtractionResult]:
        results = []
        cooldown = self._cooldown_seconds

        for _ in range(cycles):
            if use_surveys:
                surveys = self.survey(ship)
                if surveys:
                    for survey_data in surveys:
                        survey_obj = Survey(
                            signature=survey_data.deposits[0] if survey_data.deposits else "",
                            symbol=survey_data.waypoint,
                            deposits=[],
                            expiration=survey_data.expiration,
                            size=None,
                        )
                        result = self.extract_with_survey(ship, survey_obj)
                        results.append(result)
            else:
                result = self.extract(ship)
                results.append(result)

            import time

            time.sleep(cooldown)

        return results

    def get_extraction_history(
        self,
        ship_symbol: str | None = None,
        limit: int = 100,
    ) -> list[ExtractionResult]:
        history = self._extraction_history
        if ship_symbol:
            history = [e for e in history if e.ship_symbol == ship_symbol]
        return history[-limit:]

    def get_total_extracted(
        self,
        ship_symbol: str | None = None,
    ) -> dict[str, int]:
        history = self.get_extraction_history(ship_symbol)
        totals: dict[str, int] = {}
        for extraction in history:
            for mining_yield in extraction.yields:
                totals[mining_yield.good] = totals.get(mining_yield.good, 0) + mining_yield.units
        return totals


class GasSiphonBot:
    def __init__(
        self,
        fleet_api: FleetApi,
        fleet_manager: FleetManager,
        cooldown_seconds: int = 60,
    ):
        self._fleet = fleet_api
        self._fleet_manager = fleet_manager
        self._cooldown_seconds = cooldown_seconds

    def siphon(
        self,
        ship: TrackedShip,
    ):
        ship.is_busy = True
        ship.last_action = "siphoning"

        try:
            result = self._fleet.siphon_resources(ship_symbol=ship.symbol)
            return result.data
        finally:
            ship.is_busy = False

    def continuous_siphoning(
        self,
        ship: TrackedShip,
        cycles: int = 10,
    ) -> list:
        results = []

        for _ in range(cycles):
            result = self.siphon(ship)
            results.append(result)
            import time

            time.sleep(self._cooldown_seconds)

        return results


class RefiningBot:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api

    def refine(
        self,
        ship: TrackedShip,
        produce: str | None = None,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = "refining"

        try:
            if produce:
                result = self._fleet.refine(
                    ship_symbol=ship.symbol,
                    ship_refine_request={"produce": produce},
                )
            else:
                result = self._fleet.refine(ship_symbol=ship.symbol)

            produced = []
            consumed = []

            if result.data and result.data.produced:
                for item in result.data.produced:
                    produced.append({"symbol": item.symbol, "units": item.units})

            if result.data and result.data.consumed:
                for item in result.data.consumed:
                    consumed.append({"symbol": item.symbol, "units": item.units})

            return {
                "ship": ship.symbol,
                "produced": produced,
                "consumed": consumed,
            }

        finally:
            ship.is_busy = False
