import asyncio
import nest_asyncio
import tcut_to_qastle as tq
from servicex import ServiceXDataset

class ServiceXFrontend:

    def __init__(self, servicex_requests):
        """
        self._list_sx_dataset_query_pair   List of ServiceX dataset and query pair
        """
        self._list_sx_dataset_query_pair = self._load_servicex_fe(servicex_requests)

    def _load_servicex_fe(self, servicex_requests):
        """
        Setup ServiceX Frontend and return ServiceXDataset and query pairs
        """
        max_workers = 4
        ignore_cache = False
        uproot_transformer_image = "sslhep/servicex_func_adl_uproot_transformer:v1.0.0-rc.3"
        list_sx_dataset_query_pair = []
        for request in servicex_requests:        
            list_sx_dataset_query_pair.append( \
                (ServiceXDataset(dataset=request['gridDID'], backend_type='uproot', image=uproot_transformer_image, max_workers=max_workers, ignore_cache=ignore_cache), \
                tq.translate(request['ntupleName'], request['columns'], request['selection'])))
        return list_sx_dataset_query_pair

    def get_servicex_data(self, test_run = False):
        """
        
        """
        print("Retrieving data from ServiceX Uproot backend..")
        async def _get_my_data(list_query):
            return await asyncio.gather(*list_query)

        nest_asyncio.apply()

        list_query = [pair[0].get_data_parquet_async(pair[1]) for pair in self._list_sx_dataset_query_pair]
        newloop = asyncio.get_event_loop()
        data = newloop.run_until_complete(_get_my_data(list_query))
        return data