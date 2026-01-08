# -*- mode: python ; coding: utf-8 -*-
"""
BotHarbor PyInstaller spec file.

Builds a one-folder distribution for use with Inno Setup installer.
Output: dist/BotHarbor/BotHarbor.exe (plus dependencies)

To build:
    pyinstaller --noconfirm --clean botharbor.spec

Resource layout must match resource_path() in helpers.py:
- ui/styles.qss
- ui/assets/icons/*.svg
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect PySide6 Qt plugins and dependencies
pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all('PySide6')

# Application data files - must match resource_path() layout
# Resources go to dist/BotHarbor/ui/... (relative to executable)
datas = [
    ('src/botharbor/ui/styles.qss', 'ui'),
    ('src/botharbor/ui/assets', 'ui/assets'),
]
datas += pyside6_datas

# Hidden imports for dynamic imports
hiddenimports = collect_submodules('botharbor') + pyside6_hiddenimports

a = Analysis(
    ['src/botharbor/main.py'],
    pathex=['src'],
    binaries=pyside6_binaries,
    datas=datas,
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
    [],
    exclude_binaries=True,  # One-folder mode (not onefile)
    name='BotHarbor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BotHarbor',
)
