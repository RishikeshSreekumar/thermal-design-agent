# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the Thermal Design Agent desktop build.
#
# Build from the project root:
#     pyinstaller --noconfirm packaging/ThermalDesignAgent.spec
#
# Output: dist/ThermalDesignAgent/ThermalDesignAgent.exe (folder build)

import sysconfig
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, copy_metadata

ROOT = Path(SPECPATH).parent

datas = [
    (str(ROOT / "app.py"), "."),
    (str(ROOT / "assets"), "assets"),
    (str(ROOT / ".streamlit" / "config.toml"), ".streamlit"),
]
binaries = []
hiddenimports = []

# Packages with data files, native libraries or dynamic imports
for package in ("streamlit", "cadquery", "OCP", "casadi", "nlopt", "ezdxf"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

datas += copy_metadata("streamlit")

# Windows wheels repaired by delvewheel keep their DLLs in a sibling
# "<name>.libs" folder that the package loads via add_dll_directory.
SITE_PACKAGES = Path(sysconfig.get_paths()["purelib"])

for libs_dir in SITE_PACKAGES.glob("*.libs"):
    for dll in libs_dir.glob("*.dll"):
        binaries.append((str(dll), libs_dir.name))

a = Analysis(
    [str(ROOT / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=[
        "tkinter",
        "pytest",
        "IPython",
        "trame",
        "trame_client",
        "trame_server",
        "trame_vtk",
        "trame_vuetify",
        "trame_components",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ThermalDesignAgent",
    console=True,
    icon=None,
    version=str(ROOT / "packaging" / "version_info.txt"),
    upx=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="ThermalDesignAgent",
    upx=False,
)
