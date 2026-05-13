"""
download_historical_data.py
Script para descargar y guardar datos históricos en CSV
"""

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

print("\n" + "="*70)
print("DESCARGADOR DE DATOS HISTÓRICOS")
print("="*70)

# Crear carpeta para guardar datos
data_folder = "datos_descargados"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    print(f"\n✅ Carpeta creada: {data_folder}/")

# Tickers disponibles
tickers = ['AAPL', 'MSFT', 'GOOGL', 'BTC-USD', 'ETH-USD', 'SPY', 'QQQ']

print("\n📊 TICKERS DISPONIBLES:")
for i, ticker in enumerate(tickers, 1):
    print(f"   {i}. {ticker}")

# Seleccionar ticker
print("\n¿Cuál ticker quieres descargar?")
try:
    choice = int(input("Número (1-7): ")) - 1
    if 0 <= choice < len(tickers):
        ticker = tickers[choice]
    else:
        ticker = input("O ingresa un ticker personalizado (ej: TSLA, ETH-USD): ").upper()
except:
    ticker = input("Ingresa un ticker personalizado (ej: TSLA, ETH-USD): ").upper()

# Período por defecto (últimos 3 años)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')

print(f"\n📅 Período de descarga:")
print(f"   Desde: {start_date}")
print(f"   Hasta: {end_date}")

# Descargar datos
print(f"\n⏳ Descargando datos de {ticker}...")
try:
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    if df.empty:
        print(f"❌ No se encontraron datos para {ticker}")
    else:
        # Guardar en CSV
        filename = f"{data_folder}/{ticker}_{start_date}_to_{end_date}.csv"
        df.to_csv(filename)
        
        print(f"\n✅ Datos descargados exitosamente:")
        print(f"   - Archivo: {filename}")
        print(f"   - Candles: {len(df)}")
        print(f"   - Rango: {df.index.min().date()} a {df.index.max().date()}")
        print(f"   - Precio mín: ${df['Close'].min():.2f}")
        print(f"   - Precio máx: ${df['Close'].max():.2f}")
        print(f"   - Precio actual: ${df['Close'].iloc[-1]:.2f}")
        
        print(f"\n📂 Puedes abrir el archivo en Excel o cualquier programa")
        
except Exception as e:
    print(f"❌ Error descargando datos: {e}")

print("\n" + "="*70)
