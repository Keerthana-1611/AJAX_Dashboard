import os
import subprocess
import sys
import shutil

# === Configuration ===
project_dir = os.getcwd()
icon_path = os.path.join(project_dir, "logo\\Ajax-Backend-logo.ico")
entry_file = os.path.join(project_dir, "app.py")
exe_name = "Ajax-Backend"
exe_output_dir = os.path.join(os.getcwd(),"Backend-Builds")

output_dir = os.path.join(project_dir, "installer_output")
iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"  # Adjust path if needed




def build_exe():
    command = (
    f'pyinstaller --noconfirm --onefile --console --manifest elevated.manifest --distpath "{exe_output_dir}" '
    f"--hidden-import=mysql "
    f"--hidden-import=flask "
    f"--hidden-import=pymodbus "
    f"--hidden-import=flask_socketio "
    f"--hidden-import=socketio.namespace "
    f"--hidden-import=pymodbus.client.serial "
    f"--hidden-import=engineio.async_drivers.threading "
    f"--hidden-import=flask_cors "
    f"--hidden-import=pyserial "
    f"--hidden-import=webbrowser "
    f"--hidden-import=PIL.Image "
    f"--hidden-import=pystray "
    f'--hidden-import=socketio.async_drivers.threading ',
    f"--collect-submodules mysql "
    f"--collect-submodules pymodbus "
    f'--name "{exe_name}" '
    f'--icon "{icon_path}" '
    f'--add-data "{project_dir}/.venv/Lib/site-packages/mysql;mysql" '
    f'--add-data "{project_dir}/.venv/Lib/site-packages/socketio;socketio" '
    f'--add-data "{project_dir}/db_handler.py;." '
    f'--add-data "{project_dir}/modbus_handler.py;." '
    f'--add-data "{project_dir}/main.py;." '
    f'--add-data "{project_dir}/Blueprints;Blueprints" '
    f'--add-data "{project_dir}/DAQ;DAQ" '
    f'--add-data "{project_dir}/data;data" '
    f'--add-data "{project_dir}/logo;logo" '
    f'"{entry_file}" '
)

    print("[INFO] Running PyInstaller...")
    subprocess.run(command, shell=True, check=True)
    print("[SUCCESS] EXE created.")

def build_installer():
    exe_path = os.path.abspath(f"dist\\{exe_name}.exe")
    iss_script = "Builder.iss"
    print("[INFO] Running Inno Setup...")
    subprocess.run([iscc_path, iss_script], check=True)
    print(f"[SUCCESS] Installer created in: {output_dir}")

def clean_builds(type):

    """
    Delete a folder and all its contents on Windows.
    
    Parameters:
        path (str): Absolute or relative path to the folder.
    
    Returns:
        bool: True if folder was deleted successfully, False otherwise.
    """
    if type == 'exe':
        paths = ['Backend-Builds','dist','build']
    elif type == 'installer':
        paths = ['Builds']
    for path in paths:
        path = os.path.abspath(path)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"Deleted folder: {path}")
            except PermissionError:
                print(f"Permission denied: {path} (try running as admin)")
            except Exception as e:
                print(f"Error deleting folder {path}: {e}")
        else:
            print(f"Folder not found: {path}")
   
    return

def main():
    if len(sys.argv) > 3 or not (sys.argv[1] in ("clean","exe","installer")):
        print("Usage: python build.py [exe|installer|clean]")
        return

    if sys.argv[1] == "exe":
        build_exe()
    elif sys.argv[1] == "installer":
        build_installer()
    elif sys.argv[1] == "clean":
        clean_builds(sys.argv[2])
    else:
        print('invalid parameter')

if __name__ == "__main__":
    main()
