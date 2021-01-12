from pathlib import Path
# import uproot as uproot
from parquet_to_root import parquet_to_root

def make_ntuples(trex_config, sx_requests, output_parquet_list):

    if len(sx_requests) is len(output_parquet_list):
        pass
    else:
        raise ValueError('Number of requests and outputs do not agree. It might be due to the failed transformations')

    # Create output directory
    Path(trex_config.get_job_block('Job') + "/Data").mkdir(parents=True, exist_ok=True)

    # ROOT file per SAMPLE
    
    
    
    for (request, output) in zip(sx_requests, output_parquet_list):
    # for request in sx_requests:
        output_file_name = trex_config.get_job_block('Job') + "/Data/" + request['Sample'] + ".root"
        # fout = uproot.recreate( output_file_name )
        # fout.close()
        # print(output_file_name)
        for fi in output:
            parquet_to_root(fi, output_file_name, request['ntupleName'])
        # fout.close()