"""Config flow for the Miner Pool Stats integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_ACCOUNT_ID,
    CONF_ADDRESS,
    CONF_API_KEY,
    CONF_COIN_KEY,
    CONF_COIN_NAME,
    CONF_POOL_KEY,
    CONF_POOL_NAME,
    CONF_POOL_URL,
    CONF_TITLE,
    CONF_UNIQUE_ID,
    DOMAIN,
    POOL_SOURCE_CK_POOL_KEY,
    POOL_SOURCE_CK_POOL_NAME,
    POOL_SOURCE_COIN_MINERS_KEY,
    POOL_SOURCE_COIN_MINERS_NAME,
    POOL_SOURCE_F2_POOL_COINS,
    POOL_SOURCE_F2_POOL_KEY,
    POOL_SOURCE_F2_POOL_NAME,
    POOL_SOURCE_MINING_CORE_KEY,
    POOL_SOURCE_MINING_CORE_NAME,
    POOL_SOURCE_MINING_CORE_POOL_COINS,
    POOL_SOURCE_MINING_DUTCH_KEY,
    POOL_SOURCE_MINING_DUTCH_NAME,
    POOL_SOURCE_MINING_DUTCH_POOL_COINS,
    POOL_SOURCE_PUBLIC_POOL_KEY,
    POOL_SOURCE_PUBLIC_POOL_NAME,
    POOL_SOURCE_SOLO_POOL_COINS,
    POOL_SOURCE_SOLO_POOL_KEY,
    POOL_SOURCE_SOLO_POOL_NAME,
    CryptoCoin,
)
from .factory import PoolFactory
from .pool import PoolConnectionError, PoolInitData

_LOGGER = logging.getLogger(__name__)

STEP_POOL_SOURCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_POOL_KEY): SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(
                        value=POOL_SOURCE_COIN_MINERS_KEY,
                        label=POOL_SOURCE_COIN_MINERS_NAME,
                    ),
                    SelectOptionDict(
                        value=POOL_SOURCE_PUBLIC_POOL_KEY,
                        label=POOL_SOURCE_PUBLIC_POOL_NAME,
                    ),
                    SelectOptionDict(
                        value=POOL_SOURCE_F2_POOL_KEY,
                        label=POOL_SOURCE_F2_POOL_NAME,
                    ),
                    SelectOptionDict(
                        value=POOL_SOURCE_SOLO_POOL_KEY,
                        label=POOL_SOURCE_SOLO_POOL_NAME,
                    ),
                    SelectOptionDict(
                        value=POOL_SOURCE_CK_POOL_KEY,
                        label=POOL_SOURCE_CK_POOL_NAME,
                    ),
                    SelectOptionDict(
                        value=POOL_SOURCE_MINING_DUTCH_KEY,
                        label=POOL_SOURCE_MINING_DUTCH_NAME,
                    ),
                    SelectOptionDict(
                        value=POOL_SOURCE_MINING_CORE_KEY,
                        label=POOL_SOURCE_MINING_CORE_NAME,
                    ),
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        )
    }
)

STEP_PUBLIC_POOL_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_POOL_URL, default="https://public-pool.io:40557/"): str,
    }
)

STEP_WALLET_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ADDRESS): str,
    }
)


class PoolConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Miner Pool Stats."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._data: dict[str, Any] = {}

    async def validate_input(self) -> PoolInitData:
        """Validate the user input allows us to connect.

        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """

        if CONF_TITLE not in self._data:
            self._data[CONF_TITLE] = ""

        if CONF_UNIQUE_ID not in self._data:
            self._data[CONF_UNIQUE_ID] = ""

        if CONF_COIN_KEY not in self._data:
            self._data[CONF_COIN_KEY] = ""

        if CONF_COIN_NAME not in self._data:
            self._data[CONF_COIN_NAME] = ""

        pool = PoolFactory.get(self.hass, self._data)
        init_data = await pool.async_initialize(self._data)

        self._data.update(init_data)

        try:
            self._data[CONF_COIN_NAME] = CryptoCoin(self._data[CONF_COIN_KEY]).name
        except ValueError:
            self._data[CONF_COIN_NAME] = self._data[CONF_COIN_KEY]

        self._data[CONF_TITLE] = (
            f"{self._data[CONF_POOL_NAME]} - {self._data[CONF_COIN_NAME]} - {self._data[CONF_ADDRESS]}"
        )
        self._data[CONF_UNIQUE_ID] = (
            f"{self._data[CONF_POOL_KEY]}_{self._data[CONF_COIN_KEY]}_{self._data[CONF_ADDRESS].lower()}"
        )

        return PoolInitData(self._data)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_POOL_SOURCE_SCHEMA,
                errors=errors,
            )

        self._data.update(user_input)

        if user_input[CONF_POOL_KEY] == POOL_SOURCE_PUBLIC_POOL_KEY:
            self._data[CONF_POOL_NAME] = POOL_SOURCE_PUBLIC_POOL_NAME
            return await self.async_step_public_pool(user_input)

        if user_input[CONF_POOL_KEY] == POOL_SOURCE_F2_POOL_KEY:
            self._data[CONF_POOL_NAME] = POOL_SOURCE_F2_POOL_NAME
            return await self.async_step_f2_pool(user_input)

        if user_input[CONF_POOL_KEY] == POOL_SOURCE_SOLO_POOL_KEY:
            self._data[CONF_POOL_NAME] = POOL_SOURCE_SOLO_POOL_NAME
            return await self.async_step_solo_pool(user_input)

        if user_input[CONF_POOL_KEY] == POOL_SOURCE_COIN_MINERS_KEY:
            self._data[CONF_POOL_NAME] = POOL_SOURCE_COIN_MINERS_NAME
            return await self.async_step_wallet(user_input)

        if user_input[CONF_POOL_KEY] == POOL_SOURCE_CK_POOL_KEY:
            self._data[CONF_POOL_NAME] = POOL_SOURCE_CK_POOL_NAME
            return await self.async_step_ck_pool(user_input)

        if user_input[CONF_POOL_KEY] == POOL_SOURCE_MINING_DUTCH_KEY:
            self._data[CONF_POOL_NAME] = POOL_SOURCE_MINING_DUTCH_NAME
            return await self.async_step_mining_dutch_pool(user_input)

        if user_input[CONF_POOL_KEY] == POOL_SOURCE_MINING_CORE_KEY:
            self._data[CONF_POOL_NAME] = POOL_SOURCE_MINING_CORE_NAME
            return await self.async_step_mining_core_pool(user_input)

        errors["base"] = "Invalid pool source"

        return self.async_show_form(
            step_id="user", data_schema=STEP_POOL_SOURCE_SCHEMA, errors=errors
        )

    async def async_step_public_pool(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the public pool step."""
        errors: dict[str, str] = {}

        # if the user input CONF_URL is None, show the form
        if user_input is None or user_input.get(CONF_POOL_URL) is None:
            return self.async_show_form(
                step_id="public_pool",
                data_schema=STEP_PUBLIC_POOL_DATA_SCHEMA,
                errors=errors,
            )

        self._data.update(user_input)
        self._data[CONF_COIN_KEY] = CryptoCoin.BTC.value

        return await self.async_step_wallet(user_input)

    async def async_step_f2_pool(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the f2pool step."""
        errors: dict[str, str] = {}

        # if the user input CONF_URL is None, show the form
        if (
            user_input is None
            or user_input.get(CONF_COIN_KEY) is None
            or user_input.get(CONF_API_KEY) is None
        ):
            coins: list[SelectOptionDict] = [
                SelectOptionDict(value=coin.value, label=coin.name)
                for coin in POOL_SOURCE_F2_POOL_COINS
            ]

            coin_schema = vol.Schema(
                {
                    vol.Required(CONF_COIN_KEY): SelectSelector(
                        SelectSelectorConfig(
                            options=coins,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_API_KEY): str,
                }
            )

            return self.async_show_form(
                step_id="f2_pool",
                data_schema=coin_schema,
                errors=errors,
            )

        self._data.update(user_input)

        return await self.async_step_wallet(user_input)

    async def async_step_solo_pool(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the SoloPool step."""
        errors: dict[str, str] = {}

        # if the user input CONF_URL is None, show the form
        if user_input is None or user_input.get(CONF_COIN_KEY) is None:
            coins: list[SelectOptionDict] = [
                SelectOptionDict(value=coin.value, label=coin.name)
                for coin in POOL_SOURCE_SOLO_POOL_COINS
            ]

            coin_schema = vol.Schema(
                {
                    vol.Required(CONF_COIN_KEY): SelectSelector(
                        SelectSelectorConfig(
                            options=coins,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            )

            return self.async_show_form(
                step_id="solo_pool",
                data_schema=coin_schema,
                errors=errors,
            )

        self._data.update(user_input)

        return await self.async_step_wallet(user_input)

    async def async_step_ck_pool(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the ck pool step."""
        self._data[CONF_COIN_KEY] = CryptoCoin.BTC.value
        return await self.async_step_wallet(user_input)

    async def async_step_mining_dutch_pool(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the mining dutch step."""
        errors: dict[str, str] = {}

        coins: list[SelectOptionDict] = [
            SelectOptionDict(value=coin.value, label=coin.name)
            for coin in POOL_SOURCE_MINING_DUTCH_POOL_COINS
        ]

        coin_schema = vol.Schema(
            {
                vol.Required(CONF_COIN_KEY): SelectSelector(
                    SelectSelectorConfig(
                        options=coins,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_ACCOUNT_ID): str,
            }
        )

        # if the user input CONF_URL is None, show the form
        if (
            user_input is None
            or user_input.get(CONF_COIN_KEY) is None
            or user_input.get(CONF_API_KEY) is None
        ):
            return self.async_show_form(
                step_id="mining_dutch_pool",
                data_schema=coin_schema,
                errors=errors,
            )

        user_input[CONF_ADDRESS] = user_input[CONF_ACCOUNT_ID]
        self._data.update(user_input)

        result = await self._create_entry(errors)

        if result is None:
            return self.async_show_form(
                step_id="mining_dutch_pool",
                data_schema=coin_schema,
                errors=errors,
            )

        return result

    async def async_step_mining_core_pool(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the mining core pool step."""
        errors: dict[str, str] = {}

        coins: list[SelectOptionDict] = [
            SelectOptionDict(value=coin.value, label=coin.name)
            for coin in POOL_SOURCE_MINING_CORE_POOL_COINS
        ]

        coin_schema = vol.Schema(
            {
                vol.Required(CONF_POOL_URL, default="http://umbrel.local:4000"): str,
                vol.Required(CONF_COIN_KEY): SelectSelector(
                    SelectSelectorConfig(
                        options=coins,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        # if the user input CONF_COIN_KEY or CONF_POOL_URL is None, show the form
        if (
            user_input is None
            or user_input.get(CONF_COIN_KEY) is None
            or user_input.get(CONF_POOL_URL) is None
        ):
            return self.async_show_form(
                step_id="mining_core_pool",
                data_schema=coin_schema,
                errors=errors,
            )

        self._data.update(user_input)

        return await self.async_step_wallet(user_input)

    async def async_step_wallet(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the wallet step."""
        errors: dict[str, str] = {}

        # if the user input CONF_ADDRESS is None, show the form
        if user_input is None or user_input.get(CONF_ADDRESS) is None:
            return self.async_show_form(
                step_id="wallet",
                data_schema=STEP_WALLET_DATA_SCHEMA,
                errors=errors,
            )

        self._data.update(user_input)

        result = await self._create_entry(errors)

        if result is None:
            return self.async_show_form(
                step_id="wallet", data_schema=STEP_WALLET_DATA_SCHEMA, errors=errors
            )

        return result

    async def _create_entry(self, errors: dict[str, str]) -> ConfigFlowResult | None:
        """Validate and create or return the errors."""

        try:
            pool_data = await self.validate_input()
        except PoolConnectionError:
            _LOGGER.exception("Connection exception")
            errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # abort config flow if service is already configured
            match_dict: dict[str, Any] = {
                CONF_UNIQUE_ID: pool_data.unique_id,
            }
            self._async_abort_entries_match(match_dict)

            return self.async_create_entry(
                title=pool_data.title, data=pool_data.config_data
            )

        return None
