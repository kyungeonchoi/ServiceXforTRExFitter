import re
import linecache
import json

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
                            if len(inline.split(":")) == 3: # For GridDID
                                Block[block_name+str(num)][inline.split()[0].strip(':')] = ':'.join(inline.split(":")[1:]).strip("\n").strip().strip('\"')
                            else:    
                                Block[block_name+str(num)][inline.split()[0].strip(':')] = inline.split(":")[1].strip("\n").strip().strip('\"')
                    else:
                        num += 1                    
                        break
                    inlines += 1
        return Block

def load_trex_config(confFile: str):
    """
    Load TRExFitter config file as a python dictionary
    """
    job = read_configuration(confFile, "Job")
    regions = read_configuration(confFile, "Region")
    samples = read_configuration(confFile, "Sample")
    systematics = read_configuration(confFile, "Systematic")
    return {**job, **regions, **samples, **systematics}

class LoadTRExConfig():    
    """
    Load TRExFitter config file as a python dictionary
    """
    def __init__(self, confFile:str):
        self._trex_config = load_trex_config(confFile)
    
    def view(self):
        return print(json.dumps(self._trex_config, indent=4))

    def get_job_block(self, field_name:str):
        if self._trex_config['Job0'][field_name] is not None:
            return self._trex_config['Job0'][field_name]
        raise KeyError(f'{field_name} is missing in the TRExFitter configuration file.')

    def get_lumi(self):
        lumi = self._trex_config['Job0']['Lumi'].split('%')[0].strip()
        if re.findall(r'(XXX_\w+)',lumi):
            replacements = re.findall(r'(XXX_\w+)',lumi)
            replacement_file = self._trex_config['Job0']['ReplacementFile']
            with open( replacement_file ) as replacementFile:
                for line in enumerate(replacementFile.readlines()):
                    for xxx in replacements:
                        if re.search(rf'{xxx}\b', line[1]):
                            lumi = re.sub(xxx, line[1].strip(xxx + ":").strip(), lumi)
        return float(lumi)

    def get_job_name(self):
        if self._trex_config['Job0']['Job'] is not None:
            return self._trex_config['Job0']['Job']
        raise KeyError('Job is missing in the TRExFitter configuration file.')

    def get_input_name(self):
        if self._trex_config['Job0']['InputName'] is not None:
            return self._trex_config['Job0']['InputName']
        raise KeyError('InputName is missing in the TRExFitter configuration file.')

    def get_ntuple_name(self):
        if self._trex_config['Job0']['NtupleName'] is not None:
            return self._trex_config['Job0']['NtupleName']
        raise KeyError('NtupleName is missing in the TRExFitter configuration file.')

    def get_replacement_file(self):
        if self._trex_config['Job0']['ReplacementFile'] is not None:
            return self._trex_config['Job0']['ReplacementFile']
        raise KeyError('ReplacementFile is missing in the TRExFitter configuration file.')

    def get_sample_list(self):
        sample_list = []
        for key, value in self._trex_config.items():
            if key.startswith('Sample'):
                sample_list.append(value)
        if sample_list:
            return sample_list
        raise KeyError('No Sample is defined in the TRExFitter configuration file.')

    def get_region_list(self):
        region_list = []
        for key, value in self._trex_config.items():
            if key.startswith('Region'):
                region_list.append(value)
        if region_list:
            return region_list
        raise KeyError('No Region is defined in the TRExFitter configuration file.')
    