# ServiceX for TRExFitter

## Overview

[`ServiceX`](https://github.com/ssl-hep/ServiceX), a component of the IRIS-HEP DOMA group's iDDS, is an experiment-agnostic service to enable on-demand data delivery from data lakes in different data formats, including Apache Arrow and ROOT ntuple. 

[`TRExFitter`](https://gitlab.cern.ch/TRExStats/TRExFitter) is a popular framework to perform profile likelihood fits in ATLAS experiment. It takes ROOT histograms or ntuples as input. Long turnaround time of ntuple reading for large and/or remote data would slow down the whole analysis.

`ServiceXforTRExFitter` is a python library to interface ServiceX into TRExFitter framework. It provides an alternative method to produce histograms out of ROOT ntuples. 

<!-- Primary goal is the fast delivery of histograms from ROOT ntuples, which replaces TRExFitter option `n`.  -->

Expected improvements:
<!-- - Faster turnaround: this library analyzes your TRExFitter configuration to apply preselection (or filtering) on the ntuples and deliver only necessary branches. -->
- Faster turnaround: this library analyzes your TRExFitter configuration and performs on-the-fly transformation to apply preselection (or filtering) on the ntuples and delivers only necessary branches.
- Disk space: ServiceX reads files on grid, thus no need to have a direct access to ROOT ntuples.
- Scalability: ServiceX is running on a K8s cluster which can easily scale the job.

Possible bottlenecks:
- Bad network speed between the grid site and the K8s cluster where ServiceX deployed.
- Parquet to ROOT ntuple conversion is currently being done on your PC or laptop.

<!-- ServiceX for TRExFitter is a python library 
which delivers only needed data based on the TRExFitter configuration file
to deliver only data used by TRExFitter interactively. -->


## Prerequisites

- Python 3.6, 3.7, or 3.8
- Access to an *Uproot* ServiceX endpoint. More information about ServiceX can be found at [ServiceX documentation](https://servicex.readthedocs.io/en/latest/)
- PyROOT


## Usage

### Prepare TRExFitter configuration

The following items of TRExFitter configuration need to be modified to be compatible with the library:

- In `Job` block: specify `NtuplePath` in a form of `<Output Path>/Data`
- In `Sample` block: specify NEW option `GridDID` for each `Sample`, where `GridDID` is a Rucio data indentifier which includes scope and name. 
- In `Sample` block: `NtupleFile` has to be the same name as `Sample` name

An example TRExFitter configuration can be found [here](https://github.com/kyungeonchoi/ServiceXforTRExFitter/blob/development/config/v9fit_simple.config).

N.B. Tenary operation is not supported yet

### Delivery of slimmed/skimmed ROOT ntuples
<!-- ```
from servicex_for_trexfitter import ServiceXTRExFitter
sx_trex = ServiceXTRExFitter('<TRExFitter configuration file>')
sx_trex.get_ntuples()
``` -->
The library can be loaded by the following command
```
from servicex_for_trexfitter import ServiceXTRExFitter
```

and then an instance can be created with an argument of TRExFitter configuration file.
```
sx_trex = ServiceXTRExFitter('<TRExFitter configuration file>')
```

Now you are ready to make a delivery request. 
```
sx_trex.get_ntuples()
```
It will initiate ServiceX transformation(s) based on your TRExFitter configuration, and deliver ROOT ntuples that are effectively slimmed and skimmed.

### Prepare histograms from delivered ROOT ntuples

Now you can run TRExFitter with the action `n` to read input ntuples from the delivered ROOT ntuples. 
Given that the current TRExFitter framework doesn't support `ServiceXforTRExFitter` yet, the option `GridDID` in `Sample` block has to be deleted before you run TRExFitter.


## Acknowledgements
Support for this work was provided by the the U.S. Department of Energy, Office of High Energy Physics under Grant No. DE-SC0007890