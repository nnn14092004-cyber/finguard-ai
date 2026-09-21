"""Enterprise Multi-Service Local Orchestrator for FinGuard-AI.

Supervises and concurrently spawns the FastAPI Gateway (:8000) and the
Streamlit Executive Dashboard (:8501) with headless configuration and resilient process handling.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable
DASHBOARD_FILE = ROOT_DIR / "src" / "ui" / "dashboard.py"


def run_stack() -> None:
    """Launches FastAPI and Streamlit concurrently with resilient monitoring."""
    print("=" * 85)
    print("FINGUARD-AI ENTERPRISE LOCAL SERVICE SUPERVISOR")
    print("=" * 85)
    print(f"[*] Python Interpreter : {PYTHON_EXE}")
    print(f"[*] Working Directory  : {ROOT_DIR}")
    print(f"[*] Dashboard Target   : {DASHBOARD_FILE}")
    print("=" * 85)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    # Permanently suppress Streamlit interactive prompts on headless runs
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    # 1. Start FastAPI Gateway
    api_cmd = [
        PYTHON_EXE,
        "-m",
        "uvicorn",
        "src.api.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    ]

    # 2. Start Streamlit Dashboard
    streamlit_cmd = [
        PYTHON_EXE,
        "-m",
        "streamlit",
        "run",
        str(DASHBOARD_FILE),
        "--server.port",
        "8501",
        "--server.address",
        "127.0.0.1",
        "--server.headless",
        "true",
        "--browser.serverAddress",
        "127.0.0.1",
        "--browser.gatherUsageStats",
        "false",
    ]

    print("[+] Launching FastAPI Gateway on http://127.0.0.1:8000 ...")
    api_proc = subprocess.Popen(api_cmd, cwd=str(ROOT_DIR), env=env)

    time.sleep(2)

    print(f"[+] Launching Streamlit Dashboard on http://127.0.0.1:8501 ...")
    streamlit_proc = subprocess.Popen(streamlit_cmd, cwd=str(ROOT_DIR), env=env)

    print("\n" + "=" * 85)
    print("[+] Services successfully initialized and running:")
    print("    - REST API Gateway & Swagger UI   : http://127.0.0.1:8000/docs")
    print("    - REST API Root Discovery         : http://127.0.0.1:8000/")
    print("    - Streamlit Executive Dashboard   : http://127.0.0.1:8501")
    print("=" * 85)
    print("[!] KEEP THIS TERMINAL ACTIVE. Press Ctrl+C to terminate both servers cleanly.\n")

    try:
        while True:
            time.sleep(1)
            # Only terminate if the primary FastAPI gateway exits unexpectedly
            if api_proc.poll() is not None:
                print(f"[!] FastAPI process exited with return code {api_proc.returncode}")
                break
    except KeyboardInterrupt:
        print("\n[*] Shutdown signal received (Ctrl+C). Stopping all services...")
    finally:
        if api_proc.poll() is None:
            api_proc.terminate()
        if streamlit_proc.poll() is None:
            streamlit_proc.terminate()
        print("[+] All FinGuard-AI enterprise services cleanly stopped.")


if __name__ == "__main__":
    run_stack()