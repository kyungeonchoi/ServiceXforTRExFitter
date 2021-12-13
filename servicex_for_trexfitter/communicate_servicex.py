import asyncio
import tcut_to_qastle as tq
from servicex import ServiceXDataset
from aiohttp import ClientSession
import nest_asyncio


class ServiceXFrontend:

    def __init__(self, servicex_requests):
        """
        self._list_sx_dataset_query_pair   List of ServiceX dataset and query pair
        """
        self._servicex_requests = servicex_requests

    def get_servicex_data(self, test_run=False):
        """
        Get data from ServiceX
        """
        print("Retrieving data from ServiceX Uproot backend..")

        nest_asyncio.apply()

        async def bound_get_data(sem, sx_ds, query):
            async with sem:
                return await sx_ds.get_data_parquet_async(query)

        async def _get_my_data():
            sem = asyncio.Semaphore(50)  # Limit maximum concurrent ServiceX requests
            tasks = []
            ignore_cache = False
            uproot_transformer_image = "sslhep/servicex_func_adl_uproot_transformer:develop"
            async with ClientSession() as session:
                for request in self._servicex_requests:
                    sx_ds = ServiceXDataset(dataset=request['gridDID'],
                                            image=uproot_transformer_image,
                                            session_generator=session,
                                            backend_name='uproot',
                                            ignore_cache=ignore_cache)
                    query = tq.translate(request['ntupleName'],
                                         request['columns'],
                                         request['selection'])
                    task = asyncio.ensure_future(bound_get_data(sem, sx_ds, query))
                    tasks.append(task)
                return await asyncio.gather(*tasks)

        newloop = asyncio.get_event_loop()
        data = newloop.run_until_complete(_get_my_data())
        return data
