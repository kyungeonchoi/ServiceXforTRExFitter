import json
import re

class LoadServiceXRequests():    
    """
    Prepare ServiceXDataset and query pairs from input TRExFitter config
    """
    def __init__(self, trex_config):
        self._trex_config = trex_config

        print('Load ServiceX requests..')
        # trex_config.view()
        # print(f'Ntuple name: {trex_config.get_ntuple_name()}')
        self._servicex_requests = self.prepare_requests()
        # print(self.prepare_requests())

    def prepare_requests(self):
        """
        TODO: selection from Job
        """
        request_list = []
        for region in self._trex_config.get_region_list(): ## Region
            for sample in self._trex_config.get_sample_list(): ## Sample
                req = {}
                req['Region']     = region['Region']
                req['Variable']   = region['Variable']
                req['Binning']    = region['Binning']
                req['Sample']     = sample['Sample']
                req['gridDID']    = sample['GridDID']
                req['ntupleName'] = self._trex_config.get_ntuple_name()
                req['columns']    = region['Variable'].split(",")[0] + ',' + self.get_weight_columns(self.replace_XXX(sample['MCweight']))
                # req['selection']  = sample['Selection'] + ' && ' + region['Selection']
                req['selection']  = self.replace_XXX(sample['Selection']) + ' && ' + self.replace_XXX(region['Selection'])
                request_list.append(req)
        return request_list
    

    def _multiple_replace(self, dict, text):
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

        # For each match, look-up corresponding value in dictionary
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

    def get_list_of_columns_in_selection(self, tcut_selection:str):    
        # 1st step: recognize all variable names
        ignore_patterns = { # These are supported by Qastle
            "abs" : " ",
            "(" : " ",
            ")" : " ",
            "*" : " ",
            "/" : " ",
            "+" : " ",
            "-" : " "
        }
        remove_patterns = self._multiple_replace(ignore_patterns, tcut_selection)
    #     remove_marks = re.sub('[<&>!=|-]',' ',remove_patterns)
        remove_marks = re.sub(r'[\?:<&>!=|-]',' ',remove_patterns) # Add ?, : for ternary
        variables = []
        for x in remove_marks.split():
            try:
                float(x)
            except ValueError:
                variables.append(x)
        return list(dict.fromkeys(variables)) # Remove duplicates

    
    
    def get_weight_columns(self, string):
        return ', '.join(self.get_list_of_columns_in_selection(string))

    def replace_XXX(self, selection):
        if re.findall(r'(XXX_\w+)',selection):
            replacements = re.findall(r'(XXX_\w+)',selection)
            replacement_file = self._trex_config.get_replacement_file()
            with open( replacement_file ) as replacementFile:
                for line in enumerate(replacementFile.readlines()):
                    for xxx in replacements:
                        if re.search(rf'{xxx}\b', line[1]):
                            selection = re.sub(xxx, line[1].strip(xxx + ":").rstrip(), selection)
        return selection

    def view(self):
        return print(json.dumps(self._servicex_requests, indent=4))

        # ntuple_name = self._trex_config.get_ntuple_name()
        # did_list = self._trex_config.get_did_list()
        # column_list, selection_list = self._trex_config.get_column_n_selection_list()

        # for request in selection_list():

        
    ## DID, NtupleName, selection