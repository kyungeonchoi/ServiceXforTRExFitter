from pathlib import Path
from multiprocessing import Pool, cpu_count
import pyarrow.parquet as pq
import pyarrow as pa
import tqdm
import uproot


class MakeNtuples:

    def __init__(self, trex_config):
        self._trex_config = trex_config

    def merge_same_ttree(self, results):
        list_trees = []
        for tree in results:  # extract same ntuple names
            list_trees.append(tree[0]['ntupleName'])
        list_trees = list(dict.fromkeys(list_trees))
        same_tree_dict = {}
        for tree in list_trees:
            same_tree_dict[tree] = []
        for tree in list_trees:
            for loc, outputs in enumerate(results):
                if outputs[0]['ntupleName'] == tree:
                    same_tree_dict[tree].append(loc)
        merged_results = []
        for tree in same_tree_dict:
            parquet_list = []
            tree_info = None
            for output in same_tree_dict[tree]:
                parquet_list.append(results[output][1])
                tree_info = results[output][0]
            parquet_list = [item for sublist in parquet_list for item in sublist]  # flatten
            merged_results.append((tree_info, parquet_list))
        return merged_results

    def write_root_ntuple(self, results):
        results = self.merge_same_ttree(results)

        sam = results[0][0]['Sample']
        output_file_name = f"{self._trex_config.get_job_block('NtuplePaths')}/servicex/{sam}.root"

        # Delete existing one
        file_path = Path(output_file_name)
        if file_path.exists():
            file_path.unlink()

        # Write new ROOT file
        outfile = uproot.recreate(output_file_name)
        for dataset in results:
            pq_list = [pq.read_table(file) for file in dataset[1]]
            pqtable = pa.concat_tables(pq_list)
            outfile[dataset[0]['ntupleName']] = pqtable.to_pandas()
        outfile.close()

    def make_ntuples(self, sx_requests, output_parquet_list):
        if len(sx_requests) is len(output_parquet_list):
            pass
        else:
            raise ValueError('Something went wrong.. '
                             'Number of requests and outputs do not agree.'
                             'It might be due to the failed transformations')

        print('\nConverting ServiceX delivered parquet to ROOT Ntuple..')

        # Create output directory
        Path(f"{self._trex_config.get_job_block('NtuplePaths')}/servicex").mkdir(parents=True, exist_ok=True)

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
            r = list(tqdm.tqdm(pool.imap(self.write_root_ntuple, results_ordered),
                               desc='Delivered Samples', total=len(samples), unit='sample'))

        return self._trex_config.get_job_block('NtuplePaths')
