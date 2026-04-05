@echo off
echo ==============================================
echo MOTOR DE SIMULACAO DA BALANCA
echo Iniciando injeccao de dados artificiais no Firebase.
echo Mantenha essa tela aberta para fluir pelo App.
echo ==============================================
cd /D "%~dp0\VBI_Mobile"
node firebase_simulator.js
pause
