import platform
from subprocess import call

is_windows = len(platform.win32_ver()[0]) != 0
python_name = 'python3' if platform.python_version() > '2.7' else 'python'

compile_command = [python_name, "setup.py", "build_ext", "--inplace"]
run_command = [python_name, "creature_simulation.py"]

if is_windows:
    compile_command.append("--compiler=mingw32")

if call(compile_command) == 0:
    call(run_command)
