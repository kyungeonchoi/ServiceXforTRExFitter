import time

class time_measure:
    times = {}

    def __init__(self, name):
        self.name = name

    def set_time(self, step:str):
        self.times.update({step:time.monotonic()})
    
    def print_times(self):
        col_width = 30
        print("\nSummary of durations")
        print("\tCheck ServiceX Pods:".ljust(col_width), str(round(self.times['t_check_servicex_pods'] - self.times['start'], 1))+" sec".ljust(col_width) )
        print("\tConnect to ServiceX App:".ljust(col_width), str(round(self.times['t_connect_servicex_app'] - self.times['t_check_servicex_pods'], 1))+" sec".ljust(col_width))
        print("\tPrepare Transform request:".ljust(col_width), str(round(self.times['t_prepare_request'] - self.times['t_connect_servicex_app'], 1))+" sec".ljust(col_width))
        print("\tMake Request:".ljust(col_width), str(round(self.times['t_make_request'] - self.times['t_prepare_request'], 1))+" sec".ljust(col_width))
        print("\tTransform:".ljust(col_width), str(round(self.times['t_request_complete'] - self.times['t_make_request'], 1))+" sec".ljust(col_width))
        print("\tConnect to Minio:".ljust(col_width), str(round(self.times['t_connect_minio'] - self.times['t_request_complete'], 1))+" sec".ljust(col_width))
        print("\tDownload Outputs:".ljust(col_width), str(round(self.times['t_download_outputs'] - self.times['t_connect_minio'], 1))+" sec".ljust(col_width))
        print("\tPostprocessing:".ljust(col_width), str(round(self.times['t_postprocessing'] - self.times['t_download_outputs'], 1))+" sec".ljust(col_width))
        print("\tDisconnect ServiceX Apps:".ljust(col_width), str(round(self.times['t_disconnect_apps'] - self.times['t_postprocessing'], 1))+" sec".ljust(col_width))
        print("\t","-"*col_width)
        print("\tTotal duration:".ljust(col_width), str(round(self.times['t_disconnect_apps'] - self.times['start'], 1))+" sec".ljust(col_width))