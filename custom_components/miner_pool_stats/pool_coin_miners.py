"""Sool Pool Client for the Miner Pool Stats integration."""

import json
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import CONF_COIN_KEY
from .hash import HashRate, HashRateUnit
from .pool import (
    PoolAddressData,
    PoolAddressWorkerData,
    PoolClient,
    PoolConnectionError,
)

_LOGGER = logging.getLogger(__name__)

LOOKUP_TIMEOUT: float = 10
DATA_UPDATE_TIMEOUT: float = 10
DATA_UPDATE_RETRIES: int = 3


class CoinMinersPoolClient(PoolClient):
    """Public Pool Client API."""

    _last_response: str | None = None

    async def async_initialize(self, config_data: dict[str, Any]) -> dict[str, Any]:
        """Perform async initialization of client instance."""
        data_json = await self._get_data_json()
        config_data[CONF_COIN_KEY] = data_json["currency"]
        return config_data

    async def async_get_data(self) -> PoolAddressData:
        """Get updated data from the pool."""

        data_json = await self._get_data_json()

        workers: dict[str, PoolAddressWorkerData] = {}
        for worker_json in data_json["miners"]:
            worker = PoolAddressWorkerData(
                name=worker_json["ID"],
                best_difficulty=None,
                hash_rate=float(worker_json["accepted"]),
                is_online=True,
            )

            workers[worker.name] = worker

            # convert hash rate to TH/s
            if workers[worker.name].hash_rate is not None:
                hash_rate_float = workers[worker.name].hash_rate or 0.0
                workers[worker.name].hash_rate = (
                    HashRate.from_number(hash_rate_float).to_unit(HashRateUnit.GH).value
                )

        # if there are no workers, log a warning
        if not workers:
            _LOGGER.warning(
                "No workers found for address %s", self._pool_config.address
            )

        return PoolAddressData(
            float(data_json["total"]),
            float(data_json["unpaid"]),
            None,
            len(workers),
            list(workers.values()),
        )

    async def _get_data_json(self) -> Any:
        url = f"https://pool.coin-miners.info/api/walletEx?address={self._pool_config.address}"
        _LOGGER.debug("Fetching workers from %s", url)

        try:
            async with ClientSession() as session, session.get(url) as response:
                if response.status == 200:
                    txt = await response.text()
                    if len(txt) == 0 and self._last_response:
                        txt = self._last_response
                    self._last_response = txt.replace(": ,", ": 0,")  # Fix empty values
                    return json.loads(self._last_response)
                raise PoolConnectionError(
                    f"Lookup of '{self._pool_config.address}' failed: Status code {response.status}"
                )
        except ClientError as error:
            raise PoolConnectionError(
                f"Lookup of '{self._pool_config.address}' failed: {self._get_error_message(error)}"
            ) from error
