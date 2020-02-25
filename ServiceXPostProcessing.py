import uproot
# import awkward
import pyarrow.parquet as pq
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
        output_file_name = full_config["Job0"]["Job"] + "/" + full_config["Job0"]["Job"]+"_"+full_config['Region0']['Region'] + "_histos.root"
        fout = uproot.recreate( output_file_name )

        # histograms for SAMPLE in REGION
        hist_name = full_config["Region0"]["Region"] + "_" + full_config["Sample0"]["Sample"]
        binFromVariable = False
        try:
            full_config['Region0']['Binning'].split(",")
            binFromVariable = True
            logging.info(f'Histogram binning from "Region/Variable"')
        except KeyError:
            logging.info(f'Histogram binning from "Region/Binning"')
            
        if binFromVariable:
            hist_binning = full_config['Region0']['Binning'].split(",")
            h = coffea.hist.Hist("test", coffea.hist.Bin("var", "", hist_binning))
        else:
            h = coffea.hist.Hist("test", coffea.hist.Bin("var", "", int(full_config['Region0']['Variable'].split(",")[1]), float(full_config['Region0']['Variable'].split(",")[2]), float(full_config['Region0']['Variable'].split(",")[3])))

        for file in os.listdir(full_config["Job0"]["Job"]):                     
            if request_id in file:           
                # print(file)
                # columns = awkward.fromparquet(full_config["Job0"]["Job"]+"/"+file)
                # h.fill(var=numpy.array(columns[columns.columns[0]]))
                columns = pq.read_table(full_config["Job0"]["Job"]+"/"+file)
                h.fill(var=numpy.array(columns.column(0)))
        fout[hist_name] = coffea.hist.export1d(h)
                
        fout.close()