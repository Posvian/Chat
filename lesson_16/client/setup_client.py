import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "logs", "client", "unit_tests"]
}

setup(
    name="client_app",
    version="0.0.1",
    description="client_app",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client.py',
                            # base='Win32GUI',
                            target_name='client.exe')]
)
