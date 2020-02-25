# ServiceX to deliver histogram out of flat ntuple at grid for ttH ML analysis
# Requires Kubernetes cluster and ServiceX has to be deployed

import requests
from ServiceXConfig import check_servicex_pods, connect_servicex_backend, disconnect_servicex_backend
from ServiceXRequests import load_requests, print_requests, make_requests, monitor_requests
from ServiceXPostProcessing import download_output_files, output_to_histogram
from ServiceXTimer import time_measure

t = time_measure("servicex")
t.set_time("start")

# Helm chart name of ServiceX
servicex_helm_chart_name = "uproot"


# Step 1: Check SerivceX pods
check_servicex_pods(servicex_helm_chart_name)
t.set_time("t_check_servicex_pods")


# Step 2: Prepare backend to make a request
servicex_app = connect_servicex_backend(servicex_helm_chart_name, "servicex-app", 5000)
t.set_time("t_connect_servicex_app")


# Step 3: Prepare transform requests
servicex_request, full_config = load_requests("configFiles/v9fit_simple.config")
t.set_time("t_prepare_request")


# Step 4: Make requests
request_id = make_requests(servicex_request)
t.set_time("t_make_request")


# Step 5: Monitor jobs
finished_id = monitor_requests(request_id) # Returns request id of finished job
t.set_time("t_request_complete")


# Step 6: Prepare backend to download output
minio_backend = connect_servicex_backend(servicex_helm_chart_name, "minio", 9000)
t.set_time("t_connect_minio")


# Step 7: Download output
download_file_list = download_output_files(full_config,request_id)
t.set_time("t_download_outputs")


# Step 8: Post processing
output_to_histogram(servicex_request, full_config, request_id)
t.set_time("t_postprocessing")


# Step 9: Disconnect from backends
disconnect_servicex_backend(servicex_app)
disconnect_servicex_backend(minio_backend)
t.set_time("t_disconnect_apps")

t.print_times()