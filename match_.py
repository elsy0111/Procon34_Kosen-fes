import subprocess

find_process = ["pwsh", "-Command", "Get-Process",  "-Name", "procon-server_win"]
kill_process = ["pwsh", "-Command", "Stop-Process", "-Name", "procon-server_win"]
run_process  = ["./server/procon-server_win", "-c", "./server/initial.json", "-start", "3s"]

def refresh_game():
    if subprocess.call(find_process):
        print("NO RUNNING!!!!!!!")
        subprocess.call(run_process)
    else:
        print("RUNNING!!!!!!!")
        subprocess.call(kill_process)
        subprocess.call(run_process)

refresh_game()
