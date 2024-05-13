@echo off
start python pub_1.py
start python pub_2.py
start python pub_3.py
start python pub_4.py
start python pub_5.py

timeout /t 2 /nobreak >nul  
start python analyser.py
