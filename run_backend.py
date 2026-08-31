import os
import sys

# If not running in .venv and .venv exists, re-exec with .venv python
root_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(root_dir, ".venv", "Scripts", "python.exe")
if os.path.exists(venv_python) and sys.executable.lower() != venv_python.lower():
    import subprocess
    sys.exit(subprocess.call([venv_python, __file__] + sys.argv[1:]))

# Ensure UTF-8 on Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import uvicorn

if __name__ == "__main__":
    # Add backend directory to sys.path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)

    print("========================================================")
    print("  [+] BloodReach BD -- Starting Full-Stack Server")
    print("  Website  : http://localhost:8000")
    print("  API Docs : http://localhost:8000/docs")
    print("  Health   : http://localhost:8000/api/health")
    print("========================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
