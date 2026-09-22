"""
launcher.py

Desktop entry point for the Thermal Design Agent executable.

Responsibilities:
- Load .env settings (next to the .exe, then the user folder)
- Start the Streamlit server on a free local port
- Open the application in the default browser
- Provide a --selftest mode for build verification

Closing the console window stops the application.
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

import config


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _open_browser_when_ready(url: str) -> None:
    health_url = url + "/_stcore/health"

    for _ in range(240):
        try:
            with urllib.request.urlopen(health_url, timeout=1):
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.5)

    print("Server did not respond. Open this address manually:", url)


def _selftest() -> int:
    """Import the full application stack and export a test STEP file."""

    import cadquery as cq
    import streamlit  # noqa: F401

    from core.llm import get_provider_name

    step_file = config.GENERATED_DIR / "selftest.step"
    cq.exporters.export(cq.Workplane("XY").box(10, 10, 2), str(step_file))

    print("LLM provider :", get_provider_name())
    print("Resources    :", config.PROJECT_ROOT)
    print("STEP export  :", step_file, step_file.stat().st_size, "bytes")
    print("SELFTEST OK")
    return 0


def _pyinstaller_hints() -> None:
    """
    Never called. Streamlit runs app.py as a script, so PyInstaller
    cannot see its imports. Importing it here lets PyInstaller's
    static analysis bundle every module app.py needs.
    """

    import app  # noqa: F401


def main() -> int:
    if "--selftest" in sys.argv:
        return _selftest()

    from streamlit.web import cli as streamlit_cli

    # Streamlit reads .streamlit/config.toml from the working directory.
    os.chdir(config.PROJECT_ROOT)

    port = _find_free_port()
    url = f"http://localhost:{port}"

    print(f"{config.APP_NAME} {config.VERSION}")
    print("Running at", url)
    print("Outputs    ", config.GENERATED_DIR)
    print("Close this window to stop the application.")

    threading.Thread(
        target=_open_browser_when_ready,
        args=(url,),
        daemon=True,
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(config.PROJECT_ROOT / "app.py"),
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.address=localhost",
        f"--server.port={port}",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
        "--client.toolbarMode=minimal",
    ]

    return streamlit_cli.main()


if __name__ == "__main__":
    sys.exit(main())
