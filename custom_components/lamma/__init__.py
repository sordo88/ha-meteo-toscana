"""The LaMMA Toscana integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_LOCATION_ID,
    CONF_LOCATION_NAME,
    DOMAIN,
    V1_ALTITUDE,
    V1_LOCATION_ID,
    V1_LOCATION_NAME,
)
from .coordinator import LammaCoordinator


PLATFORMS: list[Platform] = [
    Platform.WEATHER,
]


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up the LaMMA Toscana integration."""

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up LaMMA Toscana from a config entry."""

    location_id = entry.data.get(
        CONF_LOCATION_ID,
        V1_LOCATION_ID,
    )

    coordinator = LammaCoordinator(
        hass,
        location_id,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload LaMMA Toscana."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )


async def async_migrate_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> bool:
    """Migrate an older LaMMA config entry."""

    if config_entry.version == 1:
        hass.config_entries.async_update_entry(
            config_entry,
            version=2,
            data={
                **config_entry.data,
                CONF_LOCATION_ID: V1_LOCATION_ID,
                CONF_LOCATION_NAME: V1_LOCATION_NAME,
            },
        )

    return True