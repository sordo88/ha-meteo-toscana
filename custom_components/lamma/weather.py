"""Weather entity for LaMMA Toscana."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import (
    LammaCoordinator,
    LammaForecast,
)


def condition_to_ha(
    condition: str | None,
) -> str:
    """Convert LaMMA condition to Home Assistant condition."""

    if not condition:
        return "cloudy"

    value = condition.lower().strip()

    if "temporale" in value:
        return "lightning-rainy"

    if "neve" in value and "pioggia" in value:
        return "snowy-rainy"

    if "neve" in value:
        return "snowy"

    if "pioggia" in value:
        return "rainy"

    if value == "sereno":
        return "sunny"

    if "poco nuvoloso" in value:
        return "partlycloudy"

    if "velato" in value:
        return "partlycloudy"

    if "nuvoloso" in value:
        return "cloudy"

    return "cloudy"


def _wind_to_bearing(
    wind: str | None,
) -> str | None:
    """Convert LaMMA wind description to a compass direction."""

    if not wind:
        return None

    direction = wind.split()[0].upper()

    mapping = {
        "O": "W",
        "NO": "NW",
    }

    if direction in mapping:
        return mapping[direction]

    if direction in {
        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SW",
        "W",
        "NW",
    }:
        return direction

    return None


class LammaWeatherEntity(
    CoordinatorEntity[LammaCoordinator],
    WeatherEntity,
):
    """Represent LaMMA weather data."""

    _attr_has_entity_name = True

    _attr_native_temperature_unit = (
        UnitOfTemperature.CELSIUS
    )

    _attr_attribution = (
        "Dati del Consorzio LaMMA, rielaborati da un'integrazione "
        "indipendente e non ufficiale."
    )

    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_HOURLY
        | WeatherEntityFeature.FORECAST_DAILY
    )

    def __init__(
        self,
        coordinator: LammaCoordinator,
    ) -> None:
        """Initialize the weather entity."""

        super().__init__(coordinator)

        location_id = coordinator.location_id

        self._attr_unique_id = (
            f"{DOMAIN}_{location_id}"
        )

        self._attr_name = "Meteo"

        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, location_id)
            },
            "name": coordinator.data.location_name,
            "model": "Previsioni meteorologiche",
        }

    @property
    def _current_forecast(
        self,
    ) -> LammaForecast | None:
        """Return the forecast period closest to now."""

        forecasts = self.coordinator.data.hourly

        if not forecasts:
            return None

        now = dt_util.now()

        past = [
            item
            for item in forecasts
            if item.datetime is not None
            and item.datetime <= now
        ]

        if past:
            return past[-1]

        return forecasts[0]

    @property
    def condition(self) -> str:
        """Return the current weather condition."""

        current = self._current_forecast

        if current is None:
            return "cloudy"

        return condition_to_ha(
            current.condition
        )

    @property
    def native_temperature(self) -> float | None:
        """Return current temperature."""

        current = self._current_forecast

        if current is None:
            return None

        return current.temperature

    @property
    def native_apparent_temperature(
        self,
    ) -> float | None:
        """Return current apparent temperature."""

        current = self._current_forecast

        if current is None:
            return None

        return current.apparent_temperature

    @property
    def humidity(self) -> float | None:
        """Return current humidity."""

        current = self._current_forecast

        if current is None:
            return None

        return current.humidity

    @property
    def uv_index(self) -> float | None:
        """Return current UV index."""

        current = self._current_forecast

        if current is None:
            return None

        return current.uv_index

    @property
    def wind_bearing(self) -> str | None:
        """Return wind direction."""

        current = self._current_forecast

        if current is None:
            return None

        return _wind_to_bearing(
            current.wind
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional LaMMA information."""

        current = self._current_forecast

        attributes = {
            "lamma_location": (
                self.coordinator.data.location_name
            ),
            "lamma_location_id": (
                self.coordinator.data.location_id
            ),
            "lamma_updated": (
                self.coordinator.data.updated.isoformat()
                if self.coordinator.data.updated
                else None
            ),
            "sunrise": self.coordinator.data.sunrise,
            "sunset": self.coordinator.data.sunset,
        }

        if current:
            attributes.update(
                {
                    "lamma_period": current.period,
                    "lamma_wind": current.wind,
                    "apparent_temperature": (
                        current.apparent_temperature
                    ),
                    "precipitation_probability": (
                        current.precipitation_probability
                    ),
                    "uv_index": current.uv_index,
                    "snow_level": current.snow_level,
                }
            )

        return attributes

    async def async_forecast_hourly(
        self,
    ) -> list[dict]:
        """Return hourly forecast."""

        now = dt_util.now()

        forecast = []

        for item in self.coordinator.data.hourly:
            if item.datetime is None:
                continue

            if item.datetime < now:
                continue

            data = {
                "datetime": (
                    item.datetime.isoformat()
                ),
                "condition": condition_to_ha(
                    item.condition
                ),
                "native_temperature": (
                    item.temperature
                ),
                "native_apparent_temperature": (
                    item.apparent_temperature
                ),
                "humidity": item.humidity,
                "precipitation_probability": (
                    item.precipitation_probability
                ),
                "uv_index": item.uv_index,
            }

            bearing = _wind_to_bearing(
                item.wind
            )

            if bearing:
                data["wind_bearing"] = bearing

            forecast.append(data)

        return forecast

    async def async_forecast_daily(
        self,
    ) -> list[dict]:
        """Return daily forecast."""

        return [
            {
                "datetime": datetime.combine(
                    item.date,
                    datetime.min.time(),
                    tzinfo=self.coordinator.time_zone,
                ).isoformat(),
                "condition": condition_to_ha(
                    item.condition
                ),
                "native_temperature": (
                    item.temperature_max
                ),
                "native_templow": (
                    item.temperature_min
                ),
                "uv_index": item.uv_index,
            }
            for item in self.coordinator.data.daily
        ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the LaMMA weather entity."""

    coordinator: LammaCoordinator = (
        entry.runtime_data
    )

    async_add_entities(
        [
            LammaWeatherEntity(
                coordinator,
            )
        ]
    )
