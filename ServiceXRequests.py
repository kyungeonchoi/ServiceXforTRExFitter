import requests
import re
import linecache
import json
import time
import logging
from tqdm import tqdm
from ServiceXTCutToQastleWrapper import tcut_to_qastle

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

def get_selection(confFile: str):

    selection_from_region = read_configuration(confFile, "Region")['Region0']['Selection']
    selection_from_sample = read_configuration(confFile, "Sample")['Sample0']['Selection']
    selection = selection_from_region + "&&" + selection_from_sample
    if re.findall(r'(XXX_\w+)',selection):
        replacements = re.findall(r'(XXX_\w+)',selection)
        # print("Replacements: ", replacements)
        replacement_file = read_configuration(confFile, "Job")['Job0']['ReplacementFile']
        with open( replacement_file ) as replacementFile:
            for line in enumerate(replacementFile.readlines()):
                for xxx in replacements:
                    if re.search(rf'{xxx}\b', line[1]):
                        selection = re.sub(xxx, line[1].strip(xxx + ":").rstrip(), selection)
    return selection

def load_requests(confFile: str):
    """
    Prepare requests for ServiceX
    """
    job = read_configuration(confFile, "Job")
    regions = read_configuration(confFile, "Region")
    samples = read_configuration(confFile, "Sample")
    systematics = read_configuration(confFile, "Systematic")
    full_config = {**job, **regions, **samples, **systematics}
    selection = get_selection(confFile)
    variable = full_config['Region0']['Variable'].split(",")[0]
        
    request = {}

    request["did"] = full_config['Sample0']['GridDID'].split(".")[0] + "." + full_config['Sample0']['GridDID'].split(".")[1] + ":" + full_config['Sample0']['GridDID']
    request["tree-name"] = full_config['Job0']['NtupleName']
    request["selection"] = tcut_to_qastle( selection, variable )
    request["image"] = "sslhep/servicex_func_adl_uproot_transformer:pandas_to_arrow"
    request["result-destination"] = "object-store"    
    request["result-format"] = "parquet"
    request["chunk-size"] = "1000"
    request["workers"] = "6"

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
        status_endpoint = f"http://localhost:5000/servicex/transformation/{request_id}/status"
        running = False
        while not running:
            status = requests.get(status_endpoint).json()
            files_remaining = status['files-remaining']
            files_processed = status['files-processed']
            if files_processed is not None and files_remaining is not None:
                running = True
            else:
                print('Status: Creating transformer pods...', end='\r')
        status = requests.get(status_endpoint).json() 
        files_remaining = status['files-remaining']
        files_processed = status['files-processed']
        total_files = files_remaining + files_processed
        t = tqdm(total=total_files, unit='file', desc=request_id)
        job_done = False
        while not job_done:                    
            time.sleep(1)
            status = requests.get(status_endpoint).json() 
            t.update(status['files-processed'] - t.n)
            files_remaining = status['files-remaining']
            files_processed = total_files-files_remaining
            if files_remaining is not None:
                if files_remaining == 0:
                    job_done = True
                    t.close()
        print(f"\nRequest id: {request_id} is finished - {files_processed}/{total_files} files are processed")
        return request_id