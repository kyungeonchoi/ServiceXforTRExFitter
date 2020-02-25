import subprocess
import json
import logging
import psutil
import time

logging.basicConfig(level=logging.INFO)

def is_chart_running(name: str):
    """
    Check whether a helm chart with `name` is running
    """
    result = subprocess.run(['helm', 'list', '--filter', name, '-q'], stdout=subprocess.PIPE)
    if result.returncode != 0:
        return False
    if result.stdout.decode('utf-8').strip() != name:
        return False
    return True


def get_pod_status(name: str):
    """
    Get the pod status for everything that starts with name
    """
    result = subprocess.run(['kubectl', 'get', 'pod', '-o', 'json'], stdout=subprocess.PIPE)
    # print(result)
    data = json.loads(result.stdout)
    return [{'name': p['metadata']['name'], 'status': all([s['ready'] for s in p['status']['containerStatuses']])} for p in data['items'] if p['metadata']['name'].startswith(name)]


def check_servicex_pods(name: str):
    """
    Checking helm chart of ServiceX and pod status
    """
    # if not is_chart_running(name):
    #     raise BaseException(f"Helm chart is not deployed!")    
    status = get_pod_status(name)
    is_ready = all(s['status'] for s in status)
    if not is_ready:
        raise BaseException(f"ServiceX is not ready! Pod(s) are not running.")
    logging.info(f'ServiceX is up and running!')


def find_pod(helm_release_name:str, pod_name:str):
    """
    Find the pod name in the release and return the full name
    """
    pods = get_pod_status(helm_release_name)
    named_pods = [p['name'] for p in pods if p['name'].startswith(f"{helm_release_name}-{pod_name}")]
    assert len(named_pods) == 1    
    return named_pods[0]


def check_portforward_running(processName: str):
    """
    Iterate over the all the running process
    """
    for proc in psutil.process_iter():
        try:
            if "kubectl" in proc.name().lower() and processName in proc.cmdline()[2]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def connect_servicex_backend(name: str, app_name: str, port: int):
    """
    Connect ServiceX backend
    """
    if not check_portforward_running(app_name):        
        try:
            app = subprocess.Popen(["kubectl", "port-forward", find_pod(name, app_name), "{}:{}".format(port,port)], stdout=subprocess.DEVNULL)
            logging.info(f"Connect to the backend of {app_name}")
            time.sleep(2) # Wait until port-forward is being established
            return app
            
        except:
            logging.info(f"Cannot connect to the backend of {app_name}")
    else:
        logging.info(f"Already connected to the backend of {app_name}")



def disconnect_servicex_backend(connection):
    """
    Disconnect ServiceX backend
    """
    if connection:
        try:
            logging.info( "Disconnected to the backend: " + psutil.Process(connection.pid).cmdline()[2] )
            connection.kill()
        except:
            logging.info( "Cannot disconnect to the backend: " + psutil.Process(connection.pid).cmdline()[2] )
    else:
        logging.info( f"No connection exists with name: {connection}" )

# def set_times(step:str, current_time):
#     times = {}
#     times.update({step:current_time})
    
