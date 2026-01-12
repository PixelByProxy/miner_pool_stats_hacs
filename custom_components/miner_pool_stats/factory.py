"""Factory for creating PoolClient instances based on the pool source."""

from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    POOL_SOURCE_CK_POOL_KEY,
    POOL_SOURCE_COIN_MINERS_KEY,
    POOL_SOURCE_F2_POOL_KEY,
    POOL_SOURCE_MINING_CORE_KEY,
    POOL_SOURCE_MINING_DUTCH_KEY,
    POOL_SOURCE_PUBLIC_POOL_KEY,
    POOL_SOURCE_SOLO_POOL_KEY,
)
from .pool import CONF_POOL_KEY, PoolClient, PoolInitData
from .pool_ckpool import CKPoolClient
from .pool_coin_miners import CoinMinersPoolClient
from .pool_f2 import F2PoolClient
from .pool_mining_core import MiningCorePoolClient
from .pool_mining_dutch import MiningDutchPoolClient
from .pool_public import PublicPoolClient
from .pool_solo import SoloPoolClient


class PoolFactory:
    """Factory for creating PoolClient instances."""

    @staticmethod
    def get(hass: HomeAssistant, config_data: dict[str, Any]) -> PoolClient:
        """Get a PoolClient instance based on the pool source."""

        source = config_data[CONF_POOL_KEY]
        pool_config = PoolInitData(config_data)

        if source == POOL_SOURCE_COIN_MINERS_KEY:
            return CoinMinersPoolClient(hass, pool_config)
        if source == POOL_SOURCE_PUBLIC_POOL_KEY:
            return PublicPoolClient(hass, pool_config)
        if source == POOL_SOURCE_F2_POOL_KEY:
            return F2PoolClient(hass, pool_config)
        if source == POOL_SOURCE_SOLO_POOL_KEY:
            return SoloPoolClient(hass, pool_config)
        if source == POOL_SOURCE_CK_POOL_KEY:
            return CKPoolClient(hass, pool_config)
        if source == POOL_SOURCE_MINING_DUTCH_KEY:
            return MiningDutchPoolClient(hass, pool_config)
        if source == POOL_SOURCE_MINING_CORE_KEY:
            return MiningCorePoolClient(hass, pool_config)

        raise ValueError(f"Unsupported pool source: {source}")
