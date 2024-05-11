@echo off
start python listener.py
start python publisher1.py
start python publisher2.py
start python publisher3.py
start python publisher4.py
start python publisher5.py
timeout /t 2 /nobreak >nul  
start python analyser.py
