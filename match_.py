import subprocess

find_process = ["pwsh", "-Command", "Get-Process",  "-Name", "procon-server_win"]
kill_process = ["pwsh", "-Command", "Stop-Process", "-Name", "procon-server_win"]
run_process  = ["start", ".\server\procon-server_win.exe", "-c", ".\server\initial.json", "-start", "3s"]

def refresh_game():
    if subprocess.call(find_process):
        print("NO RUNNING!!!!!!!")
        print(*run_process)
        subprocess.call(run_process, shell = True)
    else:
        print("RUNNING!!!!!!!")
        subprocess.call(kill_process)
        subprocess.call(run_process, shell = True)

refresh_game()
# subprocess.call(run_process)
