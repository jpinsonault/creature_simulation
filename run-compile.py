import platform
from subprocess import call

is_windows = len(platform.win32_ver()[0]) != 0

compile_command = ["python3", "setup.py", "build_ext", "--inplace"]
run_command = ["python3", "creature_simulation.py"]

if is_windows:
    compile_command.append("--compiler=mingw32")

if call(compile_command) == 0:
    call(run_command)
