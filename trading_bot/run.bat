@echo off
REM Script de instalación y ejecución del Trading Bot

echo ====================================
echo Trading Bot - Instalación y Ejecución
echo ====================================

REM Ir al directorio del proyecto
cd /d c:\Users\juanm\Documents\IA_Project\trading_bot

REM Instalar dependencias
echo.
echo 📦 Instalando dependencias...
python -m pip install --upgrade pip setuptools wheel --quiet
python -m pip install -r requirements.txt --quiet

REM Verificar instalación
echo.
echo ✅ Verificando instalación...
python -c "import streamlit; import yfinance; import backtesting; print('✅ Todas las librerías están disponibles')"

REM Ejecutar la aplicación
echo.
echo 🚀 Iniciando Trading Bot...
streamlit run app.py

pause
