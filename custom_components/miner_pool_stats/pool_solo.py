"""Sool Pool Client for the Miner Pool Stats integration."""

import logging

from aiohttp import ClientError, ClientSession

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


class SoloPoolClient(PoolClient):
    """Public Pool Client API."""

    async def async_get_data(self) -> PoolAddressData:
        """Get updated data from the pool."""

        url = f"https://{self._pool_config.coin_key}.solopool.org/api/accounts/{self._pool_config.address}"
        _LOGGER.debug("Fetching workers from %s", url)

        try:
            async with ClientSession() as session, session.get(url) as response:
                if response.status == 200:
                    json = await response.json()

                    # create a dictionary of workers by name
                    workers: dict[str, PoolAddressWorkerData] = {}
                    for worker_name in json["workers"]:
                        worker = PoolAddressWorkerData(
                            name=worker_name,
                            best_difficulty=None,
                            hash_rate=(
                                HashRate.from_number(
                                    float(json["workers"][worker_name]["hr"])
                                )
                                .to_unit(HashRateUnit.GH)
                                .value
                            ),
                            is_online=not bool(json["workers"][worker_name]["offline"]),
                        )

                        workers[worker.name] = worker

                    # if there are no workers, log a warning
                    if not workers:
                        _LOGGER.warning(
                            "No workers found for address %s", self._pool_config.address
                        )

                    return PoolAddressData(
                        float(json["paymentsTotal"] or 0.00),
                        float(json["payments"] or 0.00),
                        None,
                        int(json["workersTotal"]),
                        list(workers.values()),
                    )

                raise PoolConnectionError(
                    f"Lookup of '{self._pool_config.address}' failed: Status code {response.status}"
                )
        except ClientError as error:
            raise PoolConnectionError(
                f"Lookup of '{self._pool_config.address}' failed: {self._get_error_message(error)}"
            ) from error
