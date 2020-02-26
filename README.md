# ServiceX for TRExFitter

## Overview
[`ServiceX`](https://github.com/ssl-hep/ServiceX), a component of the IRIS-HEP DOMA group's iDDS, is an experiment-agnostic service to enable on-demand data delivery from data lakes in different data formats, including Apache Arrow and ROOT ntuple. [`TRExFitter`](https://gitlab.cern.ch/TRExStats/TRExFitter) can take ROOT ntuples as input, which leads a quite long turnaround time for large (~TB) ntuples. In principle, ServiceX can be used to extract and deliver only necessary information based on a configuration file of TRExFitter.

## Prerequisite
You need to have an access to a Kubernetes cluster which has deployed and running *uproot* ServiceX. More information can be found at [ServiceX github](https://github.com/ssl-hep/ServiceX)

## Current version
The current version (`v0.2`) supports a simplified TRExFitter configuration file which contains one Region and one Sample. It performs very similarly to the `n` step of TRExFitter which extract histograms from flat-ntuple with selection.

## Usage
The following script runs the system
```
python ServiceXReader.py
```
which performs following steps in order:
- Step 1: Check helm chart for SerivceX is deployed and running in good condition
- Step 2: Prepare backend to make a request
- Step 3: Prepare transform requests
- Step 4: Make requests
- Step 5: Monitor jobs
- Step 6: Prepare backend to download output
- Step 7: Download output
- Step 8: Post processing
- Step 9: Disconnect from backends

You have to specify a Grid DID name for a sample in your TRExFitter configuration file.

## Example 
The following is the screen print from the example config file.
```
INFO:root:ServiceX is up and running!
INFO:root:Already connected to the backend of servicex-app
INFO:root:Number of accessed branches for the selection: 47
{
    "did": "user.kchoi:user.kchoi.ttHML_80fb_ttH",
    "tree-name": "nominal",
    "selection": "(Select ... 'MVA3lCERN_weight_ttH'))))",
    "image": "sslhep/servicex_func_adl_uproot_transformer:pandas_to_arrow",
    "result-destination": "object-store",
    "result-format": "parquet",
    "chunk-size": "1000",
    "workers": "6"
}
Press Y to submit the requests: y
15ab9f15-779e-4423-a768-dff7b6aae051: 100%|████████████████████████████| 6/6 [01:09<00:00, 11.59s/file]

Request id: 15ab9f15-779e-4423-a768-dff7b6aae051 is finished - 6/6 files are processed
INFO:root:Connect to the backend of minio
INFO:root:Merge files from request id: 15ab9f15-779e-4423-a768-dff7b6aae051
INFO:root:Histogram binning from "Region/Variable"
INFO:root:No connection exists with name: None
INFO:root:Disconnected to the backend: uproot-minio-86475d69cd-rjkp5

Summary of durations
	Check ServiceX Pods:          7.1 sec
	Connect to ServiceX App:      0.0 sec
	Prepare Transform request:    0.1 sec
	Make Request:                 7.7 sec
	Transform:                    75.4 sec
	Connect to Minio:             2.5 sec
	Download Outputs:             1.1 sec
	Postprocessing:               0.7 sec
	Disconnect ServiceX Apps:     0.0 sec
	 ------------------------------
	Total duration:               94.7 sec
```
It should create a directory `v9` which contains a ROOT file `v9_l30tau_ttH_histos.root`.