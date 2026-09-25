"""Constants for the LaMMA Toscana integration."""

from __future__ import annotations

from datetime import time

DOMAIN = "lamma"

NAME = "Meteo Toscana"

CONF_LOCATION = "location"
CONF_LOCATION_NAME = "location_name"
CONF_LOCATION_ID = "location_id"
CONF_ALTITUDE = "altitude"

# Default del Config Flow
DEFAULT_LOCATION_ID = "firenze"
DEFAULT_LOCATION_NAME = "Firenze"

# Valori della V0.1, utilizzati per la migrazione
V1_LOCATION_ID = "sancascianovaldipesa"
V1_LOCATION_NAME = "San Casciano in Val di Pesa"
V1_ALTITUDE = 300

BASE_URL = (
    "https://www.lamma.toscana.it/"
    "previ/ita/xml/comuni_web/dati/"
)

LOCALITIES_URL = (
    "https://www.lamma.toscana.it/"
    "previ/ita/xml/lista_comuni.xml"
)

SCAN_INTERVAL_MINUTES = 60

PERIOD_TIMES: dict[str, time] = {
    "notte": time(2, 0),
    "notte2": time(5, 0),
    "mattina": time(8, 0),
    "mattina2": time(11, 0),
    "pomeriggio": time(14, 0),
    "pomeriggio2": time(17, 0),
    "sera": time(20, 0),
    "sera2": time(23, 0),
}
