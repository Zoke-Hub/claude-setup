#!/usr/bin/env python3
"""Machine check for the cut-out tool: find the GPU (or CPU) and its memory, pick the precision and working size that fit,
and save them in machine.json inside the cut-out venv, where birefnet_cutout.py reads them. Run it with the cut-out
venv's Python; the setup runs it after building the venv. Run it again after a hardware change.
    <cut-out venv python> probe_machine.py            # prints one line, e.g. "mps, 16 GB: half precision at 2048, memory cap 0.85"
    <cut-out venv python> probe_machine.py --json     # prints the saved settings as JSON
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from birefnet_cutout import MACHINE, machine_profile   # noqa: E402  (also sets the memory cap before torch starts)

p = machine_profile()
MACHINE.write_text(json.dumps(p, indent=1))
if "--json" in sys.argv: print(json.dumps(p, indent=1))
else:
    cap = f", memory cap {p['mps_cap']}" if p.get("mps_cap") else ""
    print(f"{p['device']}, {p['memory_gb']:g} GB: {p['precision']} precision at {p['size']}{cap}  (saved in {MACHINE})")
