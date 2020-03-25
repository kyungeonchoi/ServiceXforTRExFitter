# ServiceX for TRExFitter

## Overview
[`ServiceX`](https://github.com/ssl-hep/ServiceX), a component of the IRIS-HEP DOMA group's iDDS, is an experiment-agnostic service to enable on-demand data delivery from data lakes in different data formats, including Apache Arrow and ROOT ntuple. [`TRExFitter`](https://gitlab.cern.ch/TRExStats/TRExFitter) can take ROOT ntuples as input, which leads a quite long turnaround time for large (~TB) ntuples. In principle, ServiceX can be used to extract and deliver only necessary information based on a configuration file of TRExFitter.

## Prerequisite
You need to have an access to a Kubernetes cluster which has deployed and running *uproot* ServiceX. More information can be found at [ServiceX github](https://github.com/ssl-hep/ServiceX)

## Current version
The current version (`v0.4`) supports a simplified TRExFitter configuration file which contains one Region and multiple Samples. It performs very similarly to the `n` step of TRExFitter which extract histograms from flat-ntuple with selection. Log file will be generated under directory `log`. The output histogram is normalized to the luminosity set by the configuration file. 

## Usage
The following script runs the `ServiceXforTRExFitter`:
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
The following shows the real-time demo of the `ServiceXforTRExFitter`: 

![](demo.gif)

The output histogram is located at `v9/Histograms/ttHML_l30tau_ttH_histos.root`. 
