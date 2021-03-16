import json
import re


class LoadServiceXRequests():
    """
    Prepare ServiceXDataset and query pairs from input TRExFitter config
    """
    def __init__(self, trex_config, output_type):
        self._trex_config = trex_config

        print('Prepare ServiceX requests..')
        self._servicex_requests = self.prepare_requests(output_type)

    def prepare_requests(self, output_type):
        """
        TODO: selection from Job block
        """
        request_list = []

        if output_type == 'ntuple':
            for sample in self._trex_config.get_sample_list():      # One ServiceX request per sample
                req = {}
                req['Sample'] = sample['Sample']
                req['gridDID'] = sample['GridDID']
                req['ntupleName'] = self._trex_config.get_ntuple_name()
                req['columns'] = ', '.join(list(dict.fromkeys((self.get_columns_in_all_region() +
                                                               self.get_columns_in_job() +
                                                               self.get_columns_in_sample(sample) +
                                                               self.get_columns_in_systematic(sample['Sample'])))))
                req['selection'] = self.get_selection(sample)
                request_list.append(req)
                for systematic in self._trex_config.get_systematic_list():
                    flag = False
                    if 'Samples' in systematic:                        
                        if sample['Sample'] in [sam.strip() for sam in self.replace_XXX(systematic['Samples']).split(',')]:
                            flag = True
                    if 'Exclude' in systematic:
                        if sample['Sample'] in [sam.strip() for sam in self.replace_XXX(systematic['Exclude']).split(',')]:
                            flag = False
                    if flag:
                        if 'NtupleNameUp' in systematic:
                            req_sys = {}
                            req_sys['Sample'] = sample['Sample']
                            req_sys['gridDID'] = sample['GridDID']
                            req_sys['ntupleName'] = systematic['NtupleNameUp']
                            req_sys['columns'] = ', '.join(list(dict.fromkeys((self.get_columns_in_all_region() +
                                                                               self.get_columns_in_job() +
                                                                               self.get_columns_in_sample(sample)))))
                            req_sys['selection'] = self.replace_XXX(sample['Selection'])
                            request_list.append(req_sys)
                        if 'NtupleNameDown' in systematic:
                            req_sys = {}
                            req_sys['Sample'] = sample['Sample']
                            req_sys['gridDID'] = sample['GridDID']
                            req_sys['ntupleName'] = systematic['NtupleNameDown']
                            req_sys['columns'] = ', '.join(list(dict.fromkeys((self.get_columns_in_all_region() +
                                                                               self.get_columns_in_job() +
                                                                               self.get_columns_in_sample(sample)))))
                            req_sys['selection'] = self.replace_XXX(sample['Selection'])
                            request_list.append(req_sys)
        elif output_type == 'histogram':
            for region in self._trex_config.get_region_list():      # Region
                for sample in self._trex_config.get_sample_list():  # Sample
                    req = {}
                    req['Region'] = region['Region']
                    req['Variable'] = region['Variable']
                    req['Binning'] = region['Binning']
                    req['Sample'] = sample['Sample']
                    req['gridDID'] = sample['GridDID']
                    req['ntupleName'] = self._trex_config.get_ntuple_name()
                    req['columns'] = region['Variable'].split(",")[0] + ',' \
                        + self.get_columns(self.replace_XXX(sample['MCweight']))
                    req['selection'] = self.replace_XXX(sample['Selection']) + ' && ' + self.replace_XXX(region['Selection'])
                    request_list.append(req)

        return request_list

    def _multiple_replace(self, dict, text):
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

        # For each match, look-up corresponding value in dictionary
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

    def get_list_of_columns_in_string(self, tcut_selection: str):        
        ignore_patterns = {  # These are supported by Qastle
            "abs": " ",
            "(": " ",
            ")": " ",
            "*": " ",
            "/": " ",
            "+": " ",
            "-": " ",
            "sqrt": " "
        }
        remove_patterns = self._multiple_replace(ignore_patterns, tcut_selection)
        remove_marks = re.sub(r'[\?:<&>!=|-]', ' ', remove_patterns)  # Add ?, : for ternary
        variables = []
        for x in remove_marks.split():
            try:
                float(x)
            except ValueError:
                variables.append(x)
        return list(dict.fromkeys(variables))  # Remove duplicates

    def get_columns(self, string):
        return ', '.join(self.get_list_of_columns_in_string(string))

    def replace_XXX(self, selection):
        if re.findall(r'(XXX_\w+)', selection):
            replacements = re.findall(r'(XXX_\w+)', selection)            
            replacement_file = self._trex_config.get_replacement_file()
            with open(replacement_file) as replacementFile:
                for line in enumerate(replacementFile.readlines()):
                    if not line[1].startswith('#'):
                        for xxx in replacements:
                            if re.search(rf'{xxx}\b', line[1]):
                                selection = re.sub(xxx, line[1].strip(xxx + ":").rstrip(), selection)
        return selection

    def get_columns_in_all_region(self):
        columns = []
        for region in self._trex_config.get_region_list():  # Region
            if 'Variable' in region:
                if not region['Variable'].split(",")[0][0].isdigit():
                    columns.append(region['Variable'].split(",")[0])
            if 'Selection' in region:
                columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(region['Selection']))
            if 'MCweight' in region:
                columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(region['MCweight']))
        return columns

    def get_columns_in_job(self):
        columns = []
        job = self._trex_config.__dict__['_trex_config']['Job0']
        if 'Selection' in job:
            columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(job['Selection']))
        if 'MCweight' in job:
            columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(job['MCweight']))
        return columns

    def get_columns_in_sample(self, sample):
        columns = []
        if 'Selection' in sample:
            columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(sample['Selection']))
        if 'MCweight' in sample:
            columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(sample['MCweight']))
        return columns

    def get_columns_in_systematic(self, sample):
        """
        Returns additional brancheds from systematics for the given sample
        """
        columns = []
        for systematic in self._trex_config.get_systematic_list():
            flag = False
            if 'Samples' in systematic:
                if sample in self.replace_XXX(systematic['Samples']).split(','):
                    flag = True
            if 'Exclude' in systematic:
                if sample in self.replace_XXX(systematic['Exclude']).split(','):
                    flag = False
            if flag:
                if 'WeightSufUp' in systematic:
                    columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(systematic['WeightSufUp']))
                if 'WeightSufDown' in systematic:
                    columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(systematic['WeightSufDown']))
                if 'WeightUp' in systematic:
                    columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(systematic['WeightUp']))
                if 'WeightDown' in systematic:
                    columns = columns + self.get_list_of_columns_in_string(self.replace_XXX(systematic['WeightDown']))
        # print(columns)
        return columns  # Duplicates will be removed in prepare_requests()

    def get_selection(self, sample):
        selection = ""
        job = self._trex_config.__dict__['_trex_config']['Job0']
        if 'Selection' in job:
            selection = self.replace_XXX(job['Selection'])
        if 'Selection' in sample:
            if selection == "":
                selection = self.replace_XXX(sample['Selection'])
            else:
                selection = selection + " && " + self.replace_XXX(sample['Selection'])
        return selection

    def view(self):
        return print(json.dumps(self._servicex_requests, indent=4))
