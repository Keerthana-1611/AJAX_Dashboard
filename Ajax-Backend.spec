# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['mysql', 'flask', 'pymodbus', 'flask_socketio', 'pymodbus.client.serial', 'engineio.async_drivers.threading', 'flask_cors', 'pyserial', 'webbrowser', 'PIL.Image', 'pystray']
hiddenimports += collect_submodules('mysql')
hiddenimports += collect_submodules('pymodbus')


a = Analysis(
    ['D:\\Production Projects\\Ajax-Backend\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\Production Projects\\Ajax-Backend/.venv/Lib/site-packages/mysql', 'mysql'), ('D:\\Production Projects\\Ajax-Backend/db_handler.py', '.'), ('D:\\Production Projects\\Ajax-Backend/modbus_handler.py', '.'), ('D:\\Production Projects\\Ajax-Backend/main.py', '.'), ('D:\\Production Projects\\Ajax-Backend/Blueprints', 'Blueprints'), ('D:\\Production Projects\\Ajax-Backend/DAQ', 'DAQ'), ('D:\\Production Projects\\Ajax-Backend/data', 'data'), ('D:\\Production Projects\\Ajax-Backend/logo', 'logo')],
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
    icon=['D:\\Production Projects\\Ajax-Backend\\logo\\Ajax-Backend-logo.ico'],
    manifest='elevated.manifest',
)
