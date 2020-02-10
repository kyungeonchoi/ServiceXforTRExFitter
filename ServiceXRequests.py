import requests
import re
import linecache
import json
import time
from tqdm import tqdm

def read_configuration(confFile: str, block_name: str):
    """
    Read TRExFitter configuration file and return block as python dict
    """
    Block = {}
    with open( confFile ) as configFile:
        num = 0
        for mark,line in enumerate(configFile.readlines()):        
            if re.search(r'\b{}\b'.format(block_name), line):            
                Block[block_name+str(num)] = {}
                Block[block_name+str(num)][line.split()[0].strip(':')] = line.split(":")[1].strip("\n").strip().strip('\"')

                inlines = mark + 2
                while inlines:
                    inline = linecache.getline(confFile, inlines)
                    if len(re.findall("^ *", inline)[0]) == 2:
                        if inline.strip(): ## Check empty line                                          
                            Block[block_name+str(num)][inline.split()[0].strip(':')] = inline.split(":")[1].strip("\n").strip().strip('\"')
                    else:
                        num += 1                    
                        break
                    inlines += 1
        return Block


def load_requests(confFile: str):
    """
    Prepare requests for ServiceX
    """
    job = read_configuration(confFile, "Job")
    regions = read_configuration(confFile, "Region")
    samples = read_configuration(confFile, "Sample")
    systematics = read_configuration(confFile, "Systematic")
    full_config = {**job, **regions, **samples, **systematics}
    
    request = {}

    request["did"] = full_config['Sample0']['GridDID'].split(".")[0] + "." + full_config['Sample0']['GridDID'].split(".")[1] + ":" + full_config['Sample0']['GridDID']
    request["tree-name"] = full_config['Job0']['NtupleName']
    request["selection"] = "(Select (call EventDataset) (lambda (list event) (list (attr event 'MVA3lCERN_weight_ttH') (attr event 'lep_ID_0') (attr event 'lep_isMedium_0'))))"
    request["image"] = "sslhep/servicex_func_adl_uproot_transformer:102_uproot_transformer"
    request["result-destination"] = "object-store"    
    request["result-format"] = "parquet"
    request["chunk-size"] = "1000"
    request["workers"] = "6"

    # ## uproot transformer example
    # request["did"] = "user.kchoi:user.kchoi.ttHML_80fb_345873_mc16a"
    # request["tree-name"] = "nominal"
    # request["selection"] = "(Select (call EventDataset) (lambda (list event) (list (attr event 'lead_jetPt') (attr event 'sublead_jetPt'))))"    
    # request["image"] = "sslhep/servicex_func_adl_uproot_transformer:102_uproot_transformer"
    # request["result-destination"] = "object-store"    
    # request["result-format"] = "parquet"
    # request["chunk-size"] = "1000"
    # request["workers"] = "2"

    ## xAOD transformer example
    # request["did"] = "mc15_13TeV:mc15_13TeV.361106.PowhegPythia8EvtGen_AZNLOCTEQ6L1_Zee.merge.DAOD_STDM3.e3601_s2576_s2132_r6630_r6264_p2363_tid05630052_00"
    # # request["did"] = "mc15_13TeV:DAOD_STDM3.05630052._000001.pool.root.1"
    # request["selection"] = "(call ResultTTree (call Select (call SelectMany (call EventDataset (list 'localds:bogus')) (lambda (list e) (call (attr e 'Jets') 'AntiKt4EMTopoJets'))) (lambda (list j) (/ (call (attr j 'pt')) 1000.0))) (list 'JetPt') 'analysis' 'junk.root')"    
    # request["image"] = "sslhep/servicex_xaod_cpp_transformer:v0.2"
    # request["result-destination"] = "object-store"
    # request["result-format"] = "root-file"    
    # request["chunk-size"] = "1000"
    # request["workers"] = "6"

    return (request, full_config)


def print_requests(request: str):
    print(json.dumps(request, indent=4))
    

def make_requests(request):
    """
    Make transform request
    """
    print_requests(request)
    char = input('Press Y to submit the requests: ')    
    if char.lower() == "y":
        response = requests.post("http://localhost:5000/servicex/transformation", json=request)  
        request_id = response.json()["request_id"]
        return request_id
    else:
        print("Do NOT submit ServiceX transform requests")
        return None


def monitor_requests(request_id):
    """
    Monitor jobs
    """
    if request_id == None:
        return None
    else:
        status_endpoint = "http://localhost:5000/servicex/transformation/{}/status".format(request_id)
        running = False
        while not running:
            time.sleep(3)
            status = requests.get(status_endpoint).json()
            files_remaining = status['files-remaining']
            files_processed = status['files-processed']
            if files_processed is not None and files_remaining is not None:
                running = True
            else:
                print(".", end=" ")
        status = requests.get(status_endpoint).json() 
        files_remaining = status['files-remaining']
        files_processed = status['files-processed']    
        t = tqdm(total=files_remaining + files_processed)
        job_done = False
        while not job_done:        
            time.sleep(1)
            status = requests.get(status_endpoint).json() 
            t.update(status['files-processed'] - t.n)
            files_remaining = status['files-remaining']
            if files_remaining is not None:
                if files_remaining == 0:
                    job_done = True
                    t.close()
        print("Job complete")
        return request_id