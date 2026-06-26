# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/steps_ide/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/steps/stdlib', 'steps/stdlib'), ('docs/QUICK-REFERENCE.md', 'docs'), ('images', 'images')],
    hiddenimports=['PyQt6.sip', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets'],
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
    [],
    exclude_binaries=True,
    name='StepsIDE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['images/Steps.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StepsIDE',
)
