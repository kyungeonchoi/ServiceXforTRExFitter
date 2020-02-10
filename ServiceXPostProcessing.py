import uproot
import awkward
import numpy
import coffea
import os
import logging
from minio import Minio
from ServiceXRequests import read_configuration, load_requests
from ServiceXConfig import connect_servicex_backend, disconnect_servicex_backend

def download_output_files(full_config, request_id: str):
    if request_id == None:
        return None
    else:
        minio_endpoint = "localhost:9000"
        minio_client = Minio(minio_endpoint,
            access_key='miniouser',
            secret_key='leftfoot1',
            secure=False)
        objects = minio_client.list_objects(request_id)
        sample_files = list([file.object_name for file in objects])    
        out_path = full_config["Job0"]["Job"]
        download_file_list = []
        for i in range(len(sample_files)):
            minio_client.fget_object(request_id, sample_files[i], f'{out_path}/{request_id}_{sample_files[i].split(":")[-1]}')
            download_file_list.append(f'{out_path}/{request_id}_{sample_files[i].split(":")[-1]}')
        return download_file_list


def output_to_histogram(servicex_request, full_config, request_id: str):
    if request_id == None:
        return
    elif servicex_request["result-format"] == "parquet":
        logging.info(f'Merge files from request id: {request_id}')

        # output_file per REGION
        output_file_name = full_config["Job0"]["Job"] + "/" + full_config["Job0"]["Job"]+"_"+full_config['Region0']['Region'] + ".root"
        fout = uproot.recreate( output_file_name )

        # histograms for SAMPLE in REGION
        hist_name = full_config["Region0"]["Region"] + "_" + full_config["Sample0"]["Sample"]
        hist_binning = full_config['Region0']['Binning'].split(",")        
        h = coffea.hist.Hist("test", coffea.hist.Bin("var", "", hist_binning))
        for file in os.listdir(full_config["Job0"]["Job"]):                     
            if request_id in file:           
                print(file)
                columns = awkward.fromparquet(full_config["Job0"]["Job"]+"/"+file)
                h.fill(var=numpy.array(columns[columns.columns[0]]))
        fout[hist_name] = coffea.hist.export1d(h)
                
        fout.close()