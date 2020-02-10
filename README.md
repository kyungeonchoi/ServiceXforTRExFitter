# ServiceX for TRExFitter

## Overview
[`ServiceX`](https://github.com/ssl-hep/ServiceX), a component of the IRIS-HEP DOMA group's iDDS, is an experiment-agnostic service to enable on-demand data delivery from data lakes in different data formats, including Apache Arrow and ROOT ntuple. [`TRExFitter`](https://gitlab.cern.ch/TRExStats/TRExFitter) can take ROOT ntuples as input, which leads a quite long turnaround time for large (~TB) ntuples. In principle, ServiceX can be used to extract and deliver only necessary information based on a configuration file of TRExFitter.

## Current version
Current version (`v0.1`) supports a very simplified version of TRExFitter configuration file.

## Prerequisite
You need to have an access to a Kubernetes cluster which has deployed and running *uproot* ServiceX. More information can be found at [ServiceX github](https://github.com/ssl-hep/ServiceX)

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



