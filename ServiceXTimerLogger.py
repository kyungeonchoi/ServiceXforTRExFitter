import time
from datetime import datetime
import logging
import subprocess
import json

# create logger
logger = logging.getLogger('servicex_logger')
logger.setLevel(logging.DEBUG)

# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create file handler and set level to debug
fh = logging.FileHandler(filename=f'logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
fh.setLevel(logging.DEBUG)

# create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s:: %(message)s')
fformatter = logging.Formatter('%(message)s')

# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(fformatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)

logger.info('Welcome to the ServiceXforTRExFitter!!')
logger.debug(f'Job submission: {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')

# # 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')


def write_transformer_log(request_id):
    result = subprocess.run(['kubectl', 'get', 'pod', '-o', 'json'], stdout=subprocess.PIPE)
    data = json.loads(result.stdout)
    transformer_list = [p['metadata']['name'] for p in data['items'] if request_id in p['metadata']['name']]
    logger.debug(f'Transformer logs:')
    for transformer in transformer_list:
        logger.debug(subprocess.run(['kubectl', 'logs', transformer], stdout=subprocess.PIPE, universal_newlines=True).stdout)


class time_measure:
    times = {}

    def __init__(self, name):
        self.name = name

    def set_time(self, step:str):
        self.times.update({step:time.monotonic()})
    
    def print_times(self):
        col_width = 30
        print("\n")
        logger.info('Summary of durations')
        logger.info("\t\tCheck ServiceX Pods:".ljust(col_width) +  f"{str(round(self.times['t_check_servicex_pods'] - self.times['start'], 1))} sec")
        logger.info("\t\tConnect to ServiceX App:".ljust(col_width) + f"{str(round(self.times['t_connect_servicex_app'] - self.times['t_check_servicex_pods'], 1))} sec")
        logger.info("\t\tPrepare Transform request:".ljust(col_width) + f"{str(round(self.times['t_prepare_request'] - self.times['t_connect_servicex_app'], 1))} sec")
        logger.info("\t\tMake Request:".ljust(col_width) + f"{str(round(self.times['t_make_request'] - self.times['t_prepare_request'], 1))} sec")
        logger.info("\t\tTransform:".ljust(col_width) + f"{str(round(self.times['t_request_complete'] - self.times['t_make_request'], 1))} sec")
        logger.info("\t\tConnect to Minio:".ljust(col_width) + f"{str(round(self.times['t_connect_minio'] - self.times['t_request_complete'], 1))} sec")
        logger.info("\t\tDownload Outputs:".ljust(col_width) + f"{str(round(self.times['t_download_outputs'] - self.times['t_connect_minio'], 1))} sec")
        logger.info("\t\tPostprocessing:".ljust(col_width) + f"{str(round(self.times['t_postprocessing'] - self.times['t_download_outputs'], 1))} sec")
        logger.info("\t\tDisconnect ServiceX Apps:".ljust(col_width) + f"{str(round(self.times['t_disconnect_apps'] - self.times['t_postprocessing'], 1))} sec")
        logger.info("\t\t" + "-"*col_width)
        logger.info("\t\tTotal duration:".ljust(col_width) + f"{str(round(self.times['t_disconnect_apps'] - self.times['start'], 1))} sec")