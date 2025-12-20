"""f2Pool Client for the Miner Pool Stats integration."""

from datetime import datetime, timedelta
import logging

from aiohttp import ClientError, ClientSession

from homeassistant.util.dt import as_utc, now

from .const import CryptoCoin
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

POOL_COIN_URI_PATHS = {
    CryptoCoin.BTC.value: "bitcoin",
    CryptoCoin.BCH.value: "bitcoin-cash",
    CryptoCoin.ALEO.value: "aleo",
    CryptoCoin.BELLS.value: "bells-mm",
    CryptoCoin.CFX.value: "conflux",
    CryptoCoin.CKB.value: "nervos",
    CryptoCoin.DASH.value: "dash",
    CryptoCoin.ELA.value: "elacoin",
    CryptoCoin.ETC.value: "ethereum-classic",
    CryptoCoin.EHHW.value: "ethw",
    CryptoCoin.FB.value: "fractal-bitcoin",
    CryptoCoin.IRON.value: "iron-fish",
    CryptoCoin.HTR.value: "hathor",
    CryptoCoin.JKC.value: "junkcoin",
    CryptoCoin.KDA.value: "kadena",
    CryptoCoin.KAS.value: "kaspa",
    CryptoCoin.LTC.value: "litecoin",
    CryptoCoin.LKY.value: "luckycoin",
    CryptoCoin.NEXA.value: "nexa",
    CryptoCoin.NMC.value: "nmccoin",
    CryptoCoin.PEP.value: "pepecoin",
    CryptoCoin.ZEC.value: "zcash",
    CryptoCoin.ZEN.value: "zen",
}


class F2PoolClient(PoolClient):
    """Public Pool Client API."""

    async def async_get_data(self) -> PoolAddressData:
        """Get updated data from the pool."""

        if self._pool_config.api_key is None:
            raise PoolConnectionError("Pool api key is not configured.")

        coin_path = POOL_COIN_URI_PATHS[self._pool_config.coin_key]
        url = f"https://api.f2pool.com/{coin_path}/{self._pool_config.address}"
        _LOGGER.debug("Fetching workers from %s", url)

        headers = {
            "F2P-API-SECRET": self._pool_config.api_key,
            "Content-Type": "application/json",
        }

        try:
            async with (
                ClientSession() as session,
                session.get(url, headers=headers) as response,
            ):
                if response.status == 200:
                    json = await response.json()

                    # create a dictionary of workers by name
                    workers: dict[str, PoolAddressWorkerData] = {}
                    for worker_arr in json["workers"]:
                        last_seen = datetime.fromisoformat(worker_arr[6])
                        current_time = as_utc(now())
                        is_online = current_time - last_seen < timedelta(minutes=30)

                        worker = PoolAddressWorkerData(
                            name=worker_arr[0],
                            best_difficulty=None,
                            hash_rate=(
                                HashRate.from_number(float(worker_arr[1]))
                                .to_unit(HashRateUnit.GH)
                                .value
                            ),
                            is_online=is_online,
                        )

                        workers[worker.name] = worker

                    # if there are no workers, log a warning
                    if not workers:
                        _LOGGER.warning(
                            "No workers found for address %s", self._pool_config.address
                        )

                    return PoolAddressData(
                        float(json["paid"]),
                        float(json["balance"]),
                        None,
                        int(json["worker_length"]),
                        list(workers.values()),
                    )

                raise PoolConnectionError(
                    f"Lookup of '{self._pool_config.address}' failed: Status code {response.status}"
                )
        except ClientError as error:
            raise PoolConnectionError(
                f"Lookup of '{self._pool_config.address}' failed: {self._get_error_message(error)}"
            ) from error
