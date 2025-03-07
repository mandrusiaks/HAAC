import logging
from datetime import timedelta
from typing import Optional
import aiohttp
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import UnitOfEnergy, UnitOfMass, UnitOfPower
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import EntityCategory
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import ApsApiClientCoordinator
from .utils import get_todays_midnight

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("username"): cv.string,
        vol.Required("password"): cv.string,
    }
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    session: aiohttp.ClientSession = async_get_clientsession(hass)
    username = config["username"]
    password = config["password"]
    coordinator = ApsApiClientCoordinator(hass, session, username, password)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities(
        [
            ApsPowerMeasurementSensor(
                coordinator,
                field="current_power",
                label="Current Power",
                icon="mdi:solar-power",
                unit=UnitOfPower.WATT
            ),
            ApsEnergySensor(
                coordinator,
                field="today_total_kwh",
                label="Today Energy",
                icon="mdi:lightning-bolt",
            ),
            # ApsEnergySensor(
            #     coordinator,
            #     field="today_co2_kg",
            #     label="co2 reduced",
            #     dev_class=SensorDeviceClass.CO2,
            #     icon="mdi:molecule-co2",
            #     unit=UnitOfMass.KILOGRAMS,
            #     entity_category=EntityCategory.DIAGNOSTIC,
            #     state_class=SensorStateClass.TOTAL_INCREASING,
            # ),
            ApsPowerMeasurementSensor(
                coordinator,
                field="system_capacity",
                label="System Capacity",
                icon="mdi:solar-power-variant",
                unit=UnitOfPower.KILO_WATT
            ),
            # ApsApiClientSensor(
            #     coordinator,
            #     field="lifetime_co2_kg",
            #     label="CO2 reduced in lifetime",
            #     dev_class=SensorDeviceClass.CO2,
            #     icon="mdi:molecule-co2",
            #     unit=UnitOfMass.KILOGRAMS,
            #     entity_category=EntityCategory.DIAGNOSTIC,
            #     state_class=SensorStateClass.TOTAL_INCREASING,
            # ),
            ApsEnergySensor(
                coordinator,
                field="month_total_kwh",
                label="Month Energy",
                icon="mdi:lightning-bolt",
            ),
            ApsEnergySensor(
                coordinator,
                field="lifetime_total_kwh",
                label="Lifetime Energy",
                icon="mdi:lightning-bolt",
            ),
            # ApsApiClientSensor(
            #     coordinator,
            #     field="tree_years",
            #     label="trees saved?",
            #     dev_class=None,
            #     icon="mdi:pine-tree",
            #     unit=None,
            #     entity_category=EntityCategory.DIAGNOSTIC,
            #     state_class=SensorStateClass.TOTAL_INCREASING,
            # ),
            ApsEnergySensor(
                coordinator,
                field="year_total_kwh",
                label="Year Energy",
                icon="mdi:lightning-bolt",
            ),
        ]
    )


class ApsPowerMeasurementSensor(CoordinatorEntity, SensorEntity):
    """Representation of an APS API client sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator,
        field,
        label,
        icon,
        unit,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.field = field
        self._label = label
        self._icon = icon
        self._state = self.coordinator.data[self.field]
        self._available = True
        self._attr_name = self._label
        self._attr_unique_id = self._label
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float:
        return round(self.coordinator.data[self.field], 1)
        
    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "idk")}, # hardcode to group all into same entity
            "name": "Solar Panels",
            "model": "ECU",
            "manufacturer": "APSystems",
        }
    

class ApsEnergyMeasurementSensor(CoordinatorEntity, SensorEntity):
    """Representation of an APS API client sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    def __init__(
        self,
        coordinator,
        field,
        label,
        icon,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.field = field
        self._label = label
        self._icon = icon
        self._available = True
        self._attr_name = self._label
        self._attr_unique_id = self._label

    @property
    def native_value(self) -> float:
        return round(self.coordinator.data[self.field], 1)
        
    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "idk")}, # hardcode to group all into same entity
            "name": "Solar Panels",
            "model": "ECU",
            "manufacturer": "APSystems",
        }

class ApsEnergySensor(CoordinatorEntity, SensorEntity):
    """Representation of an APS API client sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    def __init__(
        self,
        coordinator,
        field,
        label,
        icon,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.field = field
        self._label = label
        self._icon = icon
        self._available = True
        self._attr_name = self._label
        self._attr_unique_id = self._label

    @property
    def native_value(self) -> float:
        return round(self.coordinator.data[self.field], 1)        

    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "idk")}, # hardcode to group all into same entity
            "name": "Solar Panels",
            "model": "ECU",
            "manufacturer": "APSystems",
        }
