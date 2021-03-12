import time
from .read_trex_config import LoadTRExConfig
from .load_servicex_requests import LoadServiceXRequests
from .communicate_servicex import ServiceXFrontend
from .make_ntuples import make_ntuples


class ServiceXTRExFitter:

    def __init__(self, trex_config):
        """
        self._trex_config    Python Dict format of input TRExFitter configuration file
        """
        self._trex_config = LoadTRExConfig(trex_config)
        self._servicex_requests = LoadServiceXRequests(self._trex_config, 'ntuple')

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

    def get_ntuples(self, timer=False):
        """
        Get ROOT ntuples which contain minimal information to run the TRExFitter configuration file
        """
        
        times = {}        
        # Load ServiceX requests
        requests = self._servicex_requests.__dict__['_servicex_requests']

        # Configure ServiceX Frontend to connect ServiceX backend
        sx = ServiceXFrontend(requests)

        # Get a list of parquet files for each ServiceX request
        times.update({'t0':time.monotonic()})
        output_parquet_list = sx.get_servicex_data()
        times.update({'t1':time.monotonic()})

        # Produce ROOT ntuples
        output_path = make_ntuples(self._trex_config, requests, output_parquet_list)
        times.update({'t2':time.monotonic()})

        if timer:
            width = 50
            print("\n")
            # print("< TIMER >".center(width))
            print(f"ServiceX data delivery: {str(round(times['t1'] - times['t0'], 1))} sec".rjust(width))
            print(f"Parquet to ROOT conversion: {str(round(times['t2'] - times['t1'], 1))} sec".rjust(width))
            print("--------------------------".rjust(width))
            print(f"Total time: {str(round(times['t2'] - times['t0'], 1))} sec".rjust(width))
        print("\n")
        
        return print(f"ROOT ntuples are delivered under {output_path}")
