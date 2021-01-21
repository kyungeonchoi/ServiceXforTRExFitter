from pathlib import Path
import uproot as uproot
import pyarrow.parquet as pq
import numpy
import coffea
# import boost_histogram as bh

def make_histograms(trex_config, sx_requests, output_parquet_list):
    
    if len(sx_requests) is len(output_parquet_list):
        pass
    else:
        raise ValueError('Number of requests and outputs do not agree. It might be due to the failed transformations')

    # Create output directory
    Path(trex_config.get_job_block('Job') + "/Histograms").mkdir(parents=True, exist_ok=True)

    # ROOT file per REGION
    for region in trex_config.get_region_list():
        output_file_name = trex_config.get_job_block('Job') + "/Histograms/" + trex_config.get_job_block('InputName') + "_" + region['Region'] + "_histos.root"
        fout = uproot.recreate( output_file_name )
        binFromBinVariable = False
        try:
            region['Binning'].split(",")
            binFromBinVariable = True
            # logger.info(f'Histogram binning from "Region/Variable"')
        except KeyError:
            print(f'Histogram binning from "Region/Binning"')
            # logger.info(f'Histogram binning from "Region/Binning"')
        if binFromBinVariable:
            hist_binning = [float(s) for s in region['Binning'].split(',')]
        else:
            start = float(region['Variable'].split(",")[2])
            stop = float(region['Variable'].split(",")[3])
            bins = int(region['Variable'].split(",")[1])
            hist_binning = numpy.linspace(start, stop, bins+1).tolist()

        # histogram per SAMPLE
        for (request, output) in zip(sx_requests, output_parquet_list):
            if request['Region'] is region['Region']:
                hist_name = request['Region'] + "_" + request['Sample']
                h = coffea.hist.Hist(hist_name, coffea.hist.Bin("var", "", hist_binning))
                for outfile in output:
                    columns = pq.read_table(outfile)
                    h.fill(var=numpy.array(columns.column(request['Variable'].split(",")[0])))
                fout[hist_name] = coffea.hist.export1d(h)
        fout.close()

                
                ### Boost-histogram version
                # h = bh.Histogram(bh.axis.Variable(hist_binning))
                # for outfile in output:
                #     columns = pq.read_table(outfile)
                #     h.fill(numpy.array(columns.column(request['Variable'].split(",")[0])))
                # h*=trex_config.get_lumi()
                # fout[hist_name] = h.to_numpy()
        