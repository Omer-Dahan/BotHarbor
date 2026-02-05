# -*- mode: python ; coding: utf-8 -*-
"""
HAMAL PyInstaller spec file.

Builds a one-folder distribution for use with Inno Setup installer.
Output: dist/HAMAL/HAMAL.exe (plus dependencies)

To build:
    pyinstaller --noconfirm --clean hamal.spec

Resource layout:
- Assets are mapped to 'assets' at the root of the distribution / bundle.
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect CustomTkinter and Pillow if needed (usually auto-detected but good to ensure)
# No need to collect PySide6 as the app uses CustomTkinter (Tkinter based)

# Application data files
# Resources go to dist/HAMAL/assets/... (relative to executable root)
# Matches icons.py expectation: base / "assets" / "icons"
datas = [
    ('src/hamal/ui/assets', 'assets'),
]

# Hidden imports for dynamic imports
hiddenimports = collect_submodules('hamal')

a = Analysis(
    ['src/hamal/main.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6'], # CustomTkinter uses Tkinter, but we use PySide6 for dialogs
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # One-folder mode (not onefile)
    name='HAMAL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HAMAL',
)
