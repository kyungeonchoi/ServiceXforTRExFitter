from pathlib import Path
from parquet_to_root import parquet_to_root
from ROOT import TFile


def make_ntuples(trex_config, sx_requests, output_parquet_list):

    if len(sx_requests) is len(output_parquet_list):
        pass
    else:
        raise ValueError('Number of requests and outputs do not agree. It might be due to the failed transformations')

    print('Converting parquet to ROOT Ntuple..')

    # Create output directory
    # Path(trex_config.get_job_block('Job') + "/Data").mkdir(parents=True, exist_ok=True)
    Path(trex_config.get_job_block('NtuplePath')).mkdir(parents=True, exist_ok=True)

    # ROOT file per SAMPLE
    for (request, output) in zip(sx_requests, output_parquet_list):
        # output_file_name = trex_config.get_job_block('Job') + "/Data/" + request['Sample'] + ".root"
        output_file_name = trex_config.get_job_block('NtuplePath') + "/" + request['Sample'] + ".root"
        print(f"ntupleName: {request['ntupleName']}")

        if request['ntupleName'] != 'nominal':
            output_file = TFile.Open(output_file_name, 'UPDATE')
            parquet_to_root(output, output_file, request['ntupleName'], verbose=False)
            output_file.Close()
        else:
            parquet_to_root(output, output_file_name, request['ntupleName'], verbose=False)

    # print(f"ROOT ntuples are delivered under {trex_config.get_job_block('Job')}/Data/")
    print(f"ROOT ntuples are delivered under {trex_config.get_job_block('NtuplePath')}")
