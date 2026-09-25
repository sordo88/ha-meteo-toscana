"""Config flow for LaMMA Toscana."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .const import (
    CONF_LOCATION,
    CONF_LOCATION_ID,
    CONF_LOCATION_NAME,
    DEFAULT_LOCATION_ID,
    DOMAIN,
    LOCALITIES_URL,
)
from .localities import LammaLocality, async_get_localities


class LammaConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a LaMMA config flow."""

    VERSION = 2

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        session = async_get_clientsession(self.hass)

        try:
            localities = await async_get_localities(
                session,
                LOCALITIES_URL,
            )
        except ConnectionError:
            localities = []
            errors["base"] = "cannot_connect"
        except ValueError:
            localities = []
            errors["base"] = "invalid_data"

        if not localities:
            # Manteniamo comunque il form disponibile in caso
            # di errore nel download.
            options = [
                {
                    "value": DEFAULT_LOCATION_ID,
                    "label": DEFAULT_LOCATION_ID,
                }
            ]
        else:
            options = [
                {
                    "value": locality.location_id,
                    "label": locality.name,
                }
                for locality in localities
            ]

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOCATION,
                    default=DEFAULT_LOCATION_ID,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        if user_input is not None and not errors:
            location_id = user_input[CONF_LOCATION]

            locality = next(
                (
                    item
                    for item in localities
                    if item.location_id == location_id
                ),
                None,
            )

            if locality is None:
                errors["base"] = "invalid_location"
            else:
                await self.async_set_unique_id(
                    locality.location_id
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=locality.name,
                    data={
                        CONF_LOCATION_ID: locality.location_id,
                        CONF_LOCATION_NAME: locality.name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )