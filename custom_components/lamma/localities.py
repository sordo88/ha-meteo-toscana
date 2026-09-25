"""LaMMA locality list."""

from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET

from aiohttp import ClientError


@dataclass(frozen=True)
class LammaLocality:
    """Represent a LaMMA locality."""

    name: str
    location_id: str
    altitude: int | None = None


async def async_get_localities(
    session,
    url: str,
) -> list[LammaLocality]:
    """Download and parse the official LaMMA locality list."""

    try:
        async with session.get(
            url,
            timeout=20,
        ) as response:
            response.raise_for_status()
            xml_data = await response.read()

    except (ClientError, TimeoutError) as err:
        raise ConnectionError(
            f"Unable to download LaMMA locality list: {err}"
        ) from err

    try:
        root = ET.fromstring(xml_data)

    except ET.ParseError as err:
        raise ValueError(
            f"Unable to parse LaMMA locality list: {err}"
        ) from err

    localities: list[LammaLocality] = []

    for link in root.findall("link"):
        name = (link.findtext("title") or "").strip()
        location_id = (link.findtext("url") or "").strip()
        altitude_text = (link.findtext("quota") or "").strip()

        if not name or not location_id:
            continue

        altitude: int | None = None

        if altitude_text:
            try:
                altitude = int(altitude_text)
            except ValueError:
                altitude = None

        localities.append(
            LammaLocality(
                name=name,
                location_id=location_id,
                altitude=altitude,
            )
        )

    if not localities:
        raise ValueError(
            "No LaMMA localities found in XML"
        )

    # Ordinamento alfabetico.
    return sorted(
        localities,
        key=lambda locality: locality.name.casefold(),
    )