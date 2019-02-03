@echo off
setlocal

SET PYTHONPATH=%~dp0/analyzer;%PYTHONPATH%
python3 -m analyzer %*