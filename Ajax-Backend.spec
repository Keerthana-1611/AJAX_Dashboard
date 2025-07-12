# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['mysql', 'flask', 'pymodbus', 'flask_socketio', 'socketio.namespace', 'pymodbus.client.serial', 'engineio.async_drivers.threading', 'flask_cors', 'pyserial', 'webbrowser', 'PIL.Image', 'pystray']
hiddenimports += collect_submodules('mysql')
hiddenimports += collect_submodules('pymodbus')


a = Analysis(
    ['C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/.venv/Lib/site-packages/mysql', 'mysql'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/.venv/Lib/site-packages/socketio', 'socketio'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/db_handler.py', '.'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/modbus_handler.py', '.'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/main.py', '.'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/Blueprints', 'Blueprints'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/DAQ', 'DAQ'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/data', 'data'), ('C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard/logo', 'logo')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Ajax-Backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Lenovo1\\Desktop\\New folder\\AJAX_Dashboard\\logo\\Ajax-Backend-logo.ico'],
    manifest='elevated.manifest',
)
