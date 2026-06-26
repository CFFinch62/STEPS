# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/steps/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/steps/stdlib', 'steps/stdlib')],
    hiddenimports=['steps_repl', 'steps_repl.repl', 'steps_repl.commands', 'steps_repl.environment'],
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
    name='steps',
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
)
