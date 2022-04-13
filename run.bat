@ECHO OFF

set PYTHONPATH=src
"%~dp0venv\scripts\python.exe" -m dcs_preset_manager.app %*