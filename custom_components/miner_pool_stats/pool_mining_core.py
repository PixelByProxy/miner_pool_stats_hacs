"""Mining Core Pool Client for the Miner Pool Stats integration."""

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


class MiningCorePoolClient(PoolClient):
    """Mining Core Pool Client API."""

    async def async_get_data(self) -> PoolAddressData:
        """Get updated data from the pool."""

        if self._pool_config.pool_url is None:
            raise PoolConnectionError("Pool url is not configured.")

        url = f"{self._pool_config.pool_url.rstrip('/')}/api/pools/{self._pool_config.coin_key}/miners/{self._pool_config.address}"
        _LOGGER.debug("Fetching workers from %s", url)

        try:
            async with ClientSession() as session, session.get(url) as response:
                if response.status == 200:
                    json = await response.json()

                    # create a dictionary of workers by name
                    workers: dict[str, PoolAddressWorkerData] = {}

                    # Extract workers from the performance data
                    performance = json.get("performance", {})
                    performance_workers = performance.get("workers", {})

                    for worker_name, worker_data in performance_workers.items():
                        # Hashrate is provided in H/s, convert to GH/s
                        hashrate = float(worker_data.get("hashrate", 0))

                        worker = PoolAddressWorkerData(
                            name=worker_name,
                            best_difficulty=None,
                            hash_rate=(
                                HashRate.from_number(hashrate)
                                .to_unit(HashRateUnit.GH)
                                .value
                            ),
                            is_online=True,  # Mining Core doesn't provide online status
                        )

                        workers[worker.name] = worker

                    # if there are no workers, log a warning
                    if not workers:
                        _LOGGER.warning(
                            "No workers found for address %s", self._pool_config.address
                        )

                    return PoolAddressData(
                        float(json.get("totalPaid", 0)),
                        None,
                        None,
                        len(workers),
                        list(workers.values()),
                    )

                raise PoolConnectionError(
                    f"Lookup of '{self._pool_config.address}' failed: Status code {response.status}"
                )
        except ClientError as error:
            raise PoolConnectionError(
                f"Lookup of '{self._pool_config.address}' failed: {self._get_error_message(error)}"
            ) from error
