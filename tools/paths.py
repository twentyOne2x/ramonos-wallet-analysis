"""Portable repository code root and optional replay data workspace."""
import os, pathlib
CODE_ROOT = pathlib.Path(__file__).resolve().parents[1]
ROOT = pathlib.Path(os.environ.get('RAMONOS_RESEARCH_ROOT', CODE_ROOT)).resolve()
