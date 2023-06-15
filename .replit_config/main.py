import subprocess

subprocess.Popen(["python3", "genworlds/sockets/world_socket_server.py"],
                 stdout=subprocess.DEVNULL,
                 stderr=subprocess.STDOUT)
subprocess.Popen([
    "python3", "use_cases/roundtable/world_setup_n_launch_tree_of_thought.py"
],
                 stdout=subprocess.DEVNULL,
                 stderr=subprocess.STDOUT)
subprocess.run(["python3", "genworlds/interfaces/cli/run.py"])
