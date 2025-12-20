"""CKPool Client for the Miner Pool Stats integration."""

from datetime import datetime, timedelta
import logging

from aiohttp import ClientError, ClientSession

from homeassistant.util.dt import as_utc, now

from .hash import HashRate, HashRateUnit
from .pool import (
    PoolAddressData,
    PoolAddressWorkerData,
    PoolClient,
    PoolConnectionError,
)

_LOGGER = logging.getLogger(__name__)


class CKPoolClient(PoolClient):
    """CKPool Client API."""

    async def async_get_data(self) -> PoolAddressData:
        """Get updated data from the pool."""

        url = f"https://solo.ckpool.org/users/{self._pool_config.address}"
        _LOGGER.debug("Fetching workers from %s", url)

        try:
            async with ClientSession() as session, session.get(url) as response:
                if response.status == 200:
                    json = await response.json(content_type=None)

                    # create a dictionary of workers by name
                    workers: dict[str, PoolAddressWorkerData] = {}
                    for worker_data in json.get("worker", []):
                        workername = worker_data["workername"]
                        # If workername contains a period, use the part after it, otherwise use full name
                        worker_name = (
                            workername.split(".")[-1]
                            if "." in workername
                            else workername
                        )

                        # Worker is considered online if it has reported in the last 30 mins
                        current_time = as_utc(now())
                        last_share = as_utc(
                            datetime.fromtimestamp(worker_data["lastshare"])
                        )
                        is_online = current_time - last_share < timedelta(minutes=30)

                        workers[worker_name] = PoolAddressWorkerData(
                            worker_name,
                            float(worker_data["bestever"]),
                            (
                                HashRate.from_string(worker_data["hashrate5m"])
                                .to_unit(HashRateUnit.GH)
                                .value
                            ),
                            is_online,
                        )

                    # if there are no workers, log a warning
                    if not workers:
                        _LOGGER.warning(
                            "No workers found for address %s", self._pool_config.address
                        )

                    # Get pool total best difficulty and current hashrate
                    pool_best_diff = float(json["bestever"])

                    return PoolAddressData(
                        None,  # total_paid - not provided by API
                        None,  # current_balance - not provided by API
                        pool_best_diff,
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
