"""Data coordinator for LaMMA Toscana."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import logging
import xml.etree.ElementTree as ET

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    BASE_URL,
    DOMAIN,
    PERIOD_TIMES,
    SCAN_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class LammaForecast:
    """A single LaMMA forecast period."""

    date: date
    period: str
    datetime: datetime | None
    condition: str | None = None
    wind: str | None = None
    temperature: float | None = None
    apparent_temperature: float | None = None
    humidity: float | None = None
    precipitation_probability: float | None = None
    uv_index: float | None = None
    snow_level: float | None = None


@dataclass
class LammaDailyForecast:
    """A daily LaMMA forecast."""

    date: date
    weekday: str
    condition: str | None = None
    temperature_min: float | None = None
    temperature_max: float | None = None
    uv_index: float | None = None
    alert: str | None = None
    risks: dict[str, str] | None = None


@dataclass
class LammaData:
    """Parsed LaMMA data."""

    location_name: str
    location_id: str
    altitude: int | None
    updated: datetime | None
    sunrise: str | None
    sunset: str | None
    hourly: list[LammaForecast]
    daily: list[LammaDailyForecast]


class LammaCoordinator(DataUpdateCoordinator[LammaData]):
    """Coordinate LaMMA data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        location_id: str,
    ) -> None:
        """Initialize the coordinator."""

        self.hass = hass
        self.location_id = location_id
        self.session = async_get_clientsession(hass)

        self.forecast_url = (
            f"{BASE_URL}{location_id}.xml"
        )

        self.time_zone = dt_util.get_time_zone(
            hass.config.time_zone
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_id}",
            update_interval=timedelta(
                minutes=SCAN_INTERVAL_MINUTES
            ),
            always_update=True,
        )

    async def _async_update_data(self) -> LammaData:
        """Fetch and parse LaMMA XML data."""

        try:
            async with self.session.get(
                self.forecast_url,
                timeout=20,
            ) as response:
                response.raise_for_status()
                xml_data = await response.read()

        except (ClientError, TimeoutError) as err:
            raise UpdateFailed(
                f"Unable to download LaMMA data: {err}"
            ) from err

        try:
            return self._parse_xml(xml_data)

        except (
            ET.ParseError,
            ValueError,
            TypeError,
        ) as err:
            _LOGGER.exception(
                "Unable to parse LaMMA XML"
            )
            raise UpdateFailed(
                f"Unable to parse LaMMA XML: {err}"
            ) from err

    @staticmethod
    def _parse_float(
        value: str | None,
    ) -> float | None:
        """Parse a float safely."""

        if value is None or value == "":
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _parse_datetime(
        self,
        value: str | None,
    ) -> datetime | None:
        """Parse LaMMA local datetime."""

        if not value:
            return None

        try:
            parsed = datetime.strptime(
                value,
                "%d/%m/%Y %H:%M",
            )
        except ValueError:
            return None

        return parsed.replace(
            tzinfo=self.time_zone
        )

    def _parse_xml(
        self,
        xml_data: bytes,
    ) -> LammaData:
        """Parse LaMMA XML."""

        root = ET.fromstring(xml_data)

        location_name = (
            root.findtext("comune") or ""
        ).strip()

        location_id = (
            root.findtext("IdLocation") or ""
        ).strip()

        if not location_name:
            raise ValueError(
                "Missing location name in LaMMA XML"
            )

        if not location_id:
            raise ValueError(
                "Missing location ID in LaMMA XML"
            )

        updated = self._parse_datetime(
            root.findtext("aggiornamento")
        )

        almanacco = root.find("almanacco")

        sunrise = None
        sunset = None

        if almanacco is not None:
            sunrise = almanacco.findtext(
                "sole_sorge"
            )
            sunset = almanacco.findtext(
                "sole_tramonta"
            )

        if updated is None:
            raise ValueError(
                "Missing update date in LaMMA XML"
            )

        base_date = updated.date()

        hourly: list[LammaForecast] = []
        daily: list[LammaDailyForecast] = []

        for element in root.findall("previsione"):
            idday_text = element.attrib.get("idday")
            period = element.attrib.get("ora", "")
            weekday = element.attrib.get(
                "datadescr",
                "",
            )

            if not idday_text:
                continue

            try:
                idday = int(idday_text)
            except ValueError:
                continue

            forecast_date = (
                base_date
                + timedelta(days=idday - 1)
            )

            if period == "giorno":
                condition = None

                symbol = element.find("simbolo")

                if symbol is not None:
                    condition = symbol.attrib.get(
                        "descr"
                    )

                temperature_min = None
                temperature_max = None

                for temp in element.findall("temp"):
                    temp_type = temp.attrib.get(
                        "temp_type"
                    )

                    value = self._parse_float(
                        temp.text
                    )

                    if temp_type == "min":
                        temperature_min = value

                    elif temp_type == "max":
                        temperature_max = value

                uv_index = self._parse_float(
                    element.findtext("uv")
                )

                alert = None
                alert_element = element.find(
                    "allerta"
                )

                if alert_element is not None:
                    alert = alert_element.attrib.get(
                        "value"
                    )

                risks: dict[str, str] = {}

                for risk in element.findall(
                    "rischio"
                ):
                    description = risk.attrib.get(
                        "descr"
                    )
                    value = risk.attrib.get(
                        "value"
                    )

                    if description and value:
                        risks[description] = value

                daily.append(
                    LammaDailyForecast(
                        date=forecast_date,
                        weekday=weekday,
                        condition=condition,
                        temperature_min=temperature_min,
                        temperature_max=temperature_max,
                        uv_index=uv_index,
                        alert=alert,
                        risks=risks,
                    )
                )

                continue

            period_time = PERIOD_TIMES.get(period)

            if period_time is None:
                continue

            forecast_datetime = datetime.combine(
                forecast_date,
                period_time,
                tzinfo=self.time_zone,
            )

            condition = None
            wind = None

            for symbol in element.findall(
                "simbolo"
            ):
                image_type = symbol.attrib.get(
                    "image_type"
                )
                description = symbol.attrib.get(
                    "descr"
                )

                if image_type == "C":
                    condition = description

                elif image_type == "W":
                    wind = description

            temperature = None
            apparent_temperature = None

            for temp in element.findall("temp"):
                temp_type = temp.attrib.get(
                    "temp_type"
                )

                value = self._parse_float(
                    temp.text
                )

                if temp_type == "":
                    temperature = value

                elif temp_type == "perc":
                    apparent_temperature = value

            hourly.append(
                LammaForecast(
                    date=forecast_date,
                    period=period,
                    datetime=forecast_datetime,
                    condition=condition,
                    wind=wind,
                    temperature=temperature,
                    apparent_temperature=(
                        apparent_temperature
                    ),
                    humidity=self._parse_float(
                        element.findtext("um")
                    ),
                    precipitation_probability=(
                        self._parse_float(
                            element.findtext(
                                "prob_rain"
                            )
                        )
                    ),
                    uv_index=self._parse_float(
                        element.findtext("uv")
                    ),
                    snow_level=self._parse_float(
                        element.findtext(
                            "quota_neve"
                        )
                    ),
                )
            )

        hourly.sort(
            key=lambda item: (
                item.datetime or datetime.min.replace(
                    tzinfo=self.time_zone
                )
            )
        )

        daily.sort(
            key=lambda item: item.date
        )

        return LammaData(
            location_name=location_name,
            location_id=location_id,
            altitude=None,
            updated=updated,
            sunrise=sunrise,
            sunset=sunset,
            hourly=hourly,
            daily=daily,
        )
