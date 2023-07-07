from collections import deque
import fnmatch
from importlib import import_module
import json
from multiprocessing import Process
import os
import threading
import time
from genworlds.sockets.world_socket_client import WorldSocketClient
from genworlds.sockets.world_socket_server import start_thread

from world_setup import launch_use_case  # Assuming that launch_use_case is defined in 'another_module.py'

def get_use_case_list():
    """
    Get the list of use cases by retrieving the names of folders in the 'use_cases' directory.
    :return: JSONResponse with list of use case names
    """
    path = "use_cases"
    use_cases = [dir_name for dir_name in os.listdir(path) if os.path.isdir(os.path.join(path, dir_name))]

    world_definitions = []
    for use_case in use_cases:
        try:
            file_names = os.listdir(os.path.join(path, use_case, "world_definitions"))
        except FileNotFoundError:
            print(f"No such directory: {os.path.join(path, use_case, 'world_definitions')}")
            continue

        for file_name in file_names:
            if fnmatch.fnmatch(file_name, '*.yaml'):
                world_definitions.append({
                    "use_case": use_case,
                    "world_definition": file_name,
                })

    return world_definitions

def write_dict_to_file(dict_obj, filepath):
    with open(filepath, 'w') as f:  # 'w' for write mode
        f.write(json.dumps(dict_obj))  # convert dict to str using json.dumps
        f.write('\n')  # add a newline at the end for readability

def start_server_and_simulation(use_case, world_definition, port):

    module_name = f"use_cases.{use_case}.world_setup"
    function_name = "launch_use_case"

    module = import_module(module_name)
    launch_use_case = getattr(module, function_name)

    # start the server
    start_thread(port=port)

    # start the recorder
    file_path = os.path.join("use_cases", use_case, "world_definitions", world_definition+".mocked_record.json")
    events = []
    def process_event(event):
        events.append(event)
        write_dict_to_file({"events": events}, file_path)

    websocket_url = f"ws://127.0.0.1:{port}/ws"
    socket_recorder = WorldSocketClient(
        process_event=process_event,
        url=websocket_url,
        log_level="ERROR",
    )

    threading.Thread(
        target=socket_recorder.websocket.run_forever,
        name=f"{use_case}/{world_definition} Recorder Thread",
        daemon=True,
    ).start()

    # start the simulation
    launch_use_case(
        world_definition=world_definition, 
        yaml_data_override={"world_definition": {"base_args": {"websocket_url": websocket_url}}},
    )

def kill_process(p):
    p.terminate()
    p.join()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
    

if __name__ == '__main__':
    use_case_list = get_use_case_list()
    print(use_case_list)

    port = 10000

    running_processes = []

    parallel_processes = 5
    minutes = 30
    runtime = minutes * 60
    stagger_time = 60

    use_case_chunks = chunks(use_case_list, parallel_processes)
    for use_case_list in use_case_chunks:
        print(f"Processing {use_case_list}")
        for use_case_dict in use_case_list:
            use_case = use_case_dict["use_case"]
            world_definition = use_case_dict["world_definition"]        

            p = Process(target=start_server_and_simulation, kwargs={"use_case":use_case, "world_definition": world_definition, "port": port})
            running_processes.append(p)
            p.start()
            
            threading.Timer(runtime, kill_process, args=[p]).start()

            port += 1
            # stagger the start of each process
            time.sleep(stagger_time)
        
        time.sleep(runtime + parallel_processes*stagger_time)
    
    is_any_alive = True
    while is_any_alive:
        is_any_alive = False
        for p in running_processes:
            if p.is_alive():
                is_any_alive = True
                break
        time.sleep(1)


