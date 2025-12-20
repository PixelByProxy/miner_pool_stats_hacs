"""Mining Dutch Pool Client for the Miner Pool Stats integration."""

import logging

from aiohttp import ClientError, ClientSession

from .const import CryptoCoin
from .hash import HashRate, HashRateUnit
from .pool import (
    PoolAddressData,
    PoolAddressWorkerData,
    PoolClient,
    PoolConnectionError,
)

_LOGGER = logging.getLogger(__name__)

POOL_COIN_URI_PATHS = {
    CryptoCoin.BTC.value: "bitcoin",
    CryptoCoin.BCH.value: "bitcoincashnode",
    CryptoCoin.LTC.value: "litecoin",
}


class MiningDutchPoolClient(PoolClient):
    """Mining Dutch Pool Client API."""

    async def async_get_data(self) -> PoolAddressData:
        """Get updated data from the pool."""
        if self._pool_config.api_key is None:
            raise PoolConnectionError("Pool api key is not configured.")

        coin_path = POOL_COIN_URI_PATHS[self._pool_config.coin_key]
        url = f"https://www.mining-dutch.nl/pools/{coin_path}.php?page=api&action=getuserworkers&api_key={self._pool_config.api_key}&id={self._pool_config.address}"
        _LOGGER.debug("Fetching workers from %s", url)

        try:
            async with ClientSession() as session, session.get(url) as response:
                if response.status == 200:
                    json = await response.json(content_type=None)
                    user_data = json.get("getuserworkers", {}).get("data", {})
                    miners = user_data.get("miners", [])

                    # create a dictionary of workers by name
                    workers: dict[str, PoolAddressWorkerData] = {}
                    overall_max_difficulty = 0.0

                    for miner in miners:
                        worker_name = miner["username"]
                        # Convert the hashrate to TH/s (input is in MH/s)
                        hashrate = float(miner["hashrate"] or 0)

                        # Convert difficulty to a float, use 0 if None
                        last_max_diffculty = await self._get_max_best_difficulty(
                            worker_name
                        )
                        max_difficulty = max(
                            last_max_diffculty, float(miner["difficulty"] or 0)
                        )
                        overall_max_difficulty = max(
                            overall_max_difficulty, max_difficulty
                        )

                        # Worker is considered online if alive=1
                        is_online = bool(miner["alive"])

                        workers[worker_name] = PoolAddressWorkerData(
                            worker_name,
                            max_difficulty,
                            HashRate(hashrate, HashRateUnit.MH)
                            .to_unit(HashRateUnit.GH)
                            .value,
                            is_online,
                        )

                    # if there are no workers, log a warning
                    if not workers:
                        _LOGGER.warning(
                            "No workers found for address %s", self._pool_config.address
                        )

                    return PoolAddressData(
                        None,  # total_paid - not provided by API
                        None,  # current_balance - not provided by API
                        overall_max_difficulty,
                        len(workers),
                        list(workers.values()),
                    )

                raise PoolConnectionError(
                    f"Lookup of '{self._pool_config.address}' failed: Status code {response.status}"
                )
        except ClientError as error:
            raise PoolConnectionError(
                f"Lookup of '{self._pool_config.address}' failed: {error}"
            ) from error
