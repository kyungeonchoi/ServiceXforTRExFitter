from pathlib import Path
from parquet_to_root import parquet_to_root
from ROOT import TFile
from multiprocessing import Pool, cpu_count
import tqdm

class MakeNtuples:

    def __init__(self, trex_config):
        self._trex_config = trex_config

    def write_root_ntuple(self, results):

        sam = results[0][0]['Sample']
        # print(f"Writing Sample - {sam}")

        output_file_name = f"{self._trex_config.get_job_block('NtuplePath')}/{sam}.root"
        
        for tree in results: # loop over requests (different TTree)
            tree_name = tree[0]['ntupleName']
            out_parquet_list = tree[1]
            if tree_name != 'nominal':
                output_file = TFile.Open(output_file_name, 'UPDATE')
                parquet_to_root(out_parquet_list, output_file, tree_name, verbose=False)
                output_file.Close()
            else:
                parquet_to_root(out_parquet_list, output_file_name, tree_name, verbose=False)

    def make_ntuples(self, sx_requests, output_parquet_list):

        if len(sx_requests) is len(output_parquet_list):
            pass
        else:
            raise ValueError('Something went wrong.. '
                            'Number of requests and outputs do not agree.' 
                            'It might be due to the failed transformations')

        print('\nConverting ServiceX delivered parquet to ROOT Ntuple..')

        # Create output directory
        Path(self._trex_config.get_job_block('NtuplePath')).mkdir(parents=True, exist_ok=True)
        
        # List of Samples
        samples = list(dict.fromkeys([request['Sample'] for request in sx_requests]))

        # Pair of request and parquet output list
        result_pairs = [(request, output) for (request, output) in zip(sx_requests, output_parquet_list)]

        # dict of pairs for each sample
        results = {}
        for sample in samples:
            for pair in result_pairs:
                if pair[0]['Sample'] == sample:
                    if sample in results:
                        results[sample].append(pair)
                    else:
                        results[sample] = [pair]
        results_ordered = list(results.values())

        nproc = min(len(samples), int(cpu_count()/2))
        with Pool(processes=nproc) as pool:
            # pool.map(self.write_root_ntuple, results_ordered)
            r = list(tqdm.tqdm(pool.imap(self.write_root_ntuple, results_ordered), desc='Delivered Samples', total=len(samples), unit='sample'))

        return self._trex_config.get_job_block('NtuplePath')
