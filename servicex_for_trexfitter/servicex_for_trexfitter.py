from .read_trex_config import LoadTRExConfig
from .load_servicex_requests import LoadServiceXRequests
from .communicate_servicex import ServiceXFrontend
from .make_histograms import make_histograms
from .make_ntuples import make_ntuples

class ServiceXTRExFitter:

    def __init__(self, trex_config):
                #  sx_config = None):
        """
        self._trex_config    Python Dict format of input TRExFitter configuration file
        """
        self._trex_config = LoadTRExConfig(trex_config)
        # self._servicex_requests = LoadServiceXRequests(self._trex_config)

    def get_trex_configuration(self):
        """
        Return input TRExFitter configuration file as python dict
        """
        return self._trex_config.__dict__['_trex_config']
    
    def view_trex_configuration(self):
        """
        Return input TRExFitter configuration file as python dict
        """
        return self._trex_config.view()

    def get_histograms(self, test_run=False):
        """
        Read input ntuples and produce histograms based on TRExFitter configuration file
        """
        self._servicex_requests = LoadServiceXRequests(self._trex_config, 'histogram')
        requests = self._servicex_requests.__dict__['_servicex_requests']

        # Configure ServiceX Frontend to connect ServiceX backend
        sx = ServiceXFrontend(requests)

        # Get a list of parquet files for each ServiceX request
        output_parquet_list = sx.get_servicex_data()

        # Produce ROOT histograms
        make_histograms(self._trex_config, requests, output_parquet_list)

        # return output_parquet_list
        return 'Histograms are delivered!'
    
    def get_ntuples(self, test_run=False):
        """
        Read input ntuples and produce histograms based on TRExFitter configuration file
        """

        self._servicex_requests = LoadServiceXRequests(self._trex_config, 'ntuple')
        requests = self._servicex_requests.__dict__['_servicex_requests']

        # Configure ServiceX Frontend to connect ServiceX backend
        sx = ServiceXFrontend(requests)

        # Get a list of parquet files for each ServiceX request
        output_parquet_list = sx.get_servicex_data()

        # Produce ROOT histograms
        make_ntuples(self._trex_config, requests, output_parquet_list)

        # return requests
        # return output_parquet_list
        return 'Ntuples are delivered!'
    