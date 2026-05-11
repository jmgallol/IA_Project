# Trading Bot - Sistema de Backtesting Algorítmico

## 📖 Descripción del Proyecto

**Trading Bot** es un sistema completo de backtesting y optimización de estrategias de trading algorítmico, construido con Python, Streamlit y tecnología de punta en análisis técnico.

### Características principales:

✅ **Descarga de datos históricos** en tiempo real con yfinance  
✅ **Indicadores técnicos avanzados** (RSI, MACD, Bollinger Bands, SMA)  
✅ **Tres estrategias de trading** implementadas y personalizables  
✅ **Motor de backtesting** realista con comisiones y ejecución al cierre  
✅ **Optimización automática** de parámetros por grid search  
✅ **Visualizaciones interactivas** con Plotly (gráficos de velas, equity curve, puntos de trade)  
✅ **Interfaz intuitiva** con Streamlit  
✅ **Métricas detalladas** (Sharpe Ratio, Drawdown máximo, Win Rate, etc.)

---

## 🛠️ Instalación

### Requisitos previos:
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación:

1. **Clona o descarga el proyecto:**
```bash
cd trading_bot
```

2. **Crea un entorno virtual (recomendado):**
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución

Para iniciar la aplicación Streamlit:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador por defecto en `http://localhost:8501`

---

## 📂 Estructura del Proyecto

```
trading_bot/
│
├── app.py                          # Punto de entrada principal — ejecuta la interfaz Streamlit
│
├── config/
│   └── settings.py                 # Constantes globales, colores, parámetros iniciales
│
├── data/
│   └── loader.py                   # Descarga y limpieza de datos con yfinance
│
├── indicators/
│   └── technical.py                # Cálculo de indicadores técnicos (RSI, MACD, Bollinger, SMA)
│
├── strategies/
│   ├── rsi_strategy.py             # Estrategia basada en RSI
│   ├── sma_strategy.py             # Estrategia de cruce de medias móviles
│   └── macd_strategy.py            # Estrategia basada en MACD
│
├── backtest/
│   ├── engine.py                   # Motor de ejecución del backtesting
│   └── optimizer.py                # Optimización de parámetros (grid search)
│
├── ui/
│   ├── sidebar.py                  # Panel lateral con controles de entrada
│   ├── charts.py                   # Visualizaciones interactivas con Plotly
│   └── metrics.py                  # Renderizado de métricas y tablas
│
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Este archivo
```

---

## 📚 Descripción de Módulos

### **config/settings.py**
Define constantes globales del sistema:
- Tickers por defecto (AAPL, MSFT, BTC-USD, etc.)
- Rangos de fechas por defecto
- Parámetros de optimización para cada estrategia
- Paleta de colores del tema visual

### **data/loader.py**
Módulo de descarga y limpieza de datos:
- Función `download_data()`: descarga históricos con yfinance
- Renombra columnas al formato requerido por backtesting.py
- Elimina valores nulos
- Maneja errores personalizados (`DataNotFoundError`)

### **indicators/technical.py**
Cálculo de indicadores técnicos con pandas-ta:
- RSI (14 periodos)
- MACD con línea de señal
- Bandas de Bollinger
- SMA 20 y SMA 50
- EMA para MACD

### **strategies/rsi_strategy.py**
Estrategia basada en RSI:
- Compra cuando RSI < rsi_lower (sobreventa)
- Vende cuando RSI > rsi_upper (sobrecompra)
- Parámetros optimizables: rsi_lower, rsi_upper

### **strategies/sma_strategy.py**
Estrategia de cruce de medias móviles:
- Compra en cruce alcista (SMA corta cruza arriba SMA larga)
- Vende en cruce bajista
- Parámetros optimizables: n_short, n_long

### **strategies/macd_strategy.py**
Estrategia basada en MACD:
- Compra cuando MACD cruza arriba la línea de señal
- Vende cuando MACD cruza abajo la línea de señal
- Parámetros optimizables: fast, slow, signal

### **backtest/engine.py**
Motor de backtesting:
- Función `run_backtest()`: ejecuta un backtest con parámetros específicos
- Utiliza backtesting.py como base
- Comisión de 0.1% por operación (realismo)
- Trade on close para mayor realismo

### **backtest/optimizer.py**
Optimización de parámetros:
- Función `run_optimization()`: grid search exhaustivo
- Maximiza Sharpe Ratio
- Muestra barra de progreso en la interfaz
- Retorna mejores parámetros y estadísticas

### **ui/sidebar.py**
Panel lateral de configuración:
- Selector de ticker
- Date pickers para rango de fechas
- Selectbox de estrategia
- Slider de capital inicial
- Checkbox para optimización
- Botón de ejecución

### **ui/charts.py**
Visualizaciones interactivas:
- `plot_candlestick()`: gráfico de velas con indicadores superpuestos
- `plot_equity_curve()`: evolución del capital
- `plot_trades()`: precio con puntos de entrada/salida
- Todos los gráficos con tema dark y colores personalizados

### **ui/metrics.py**
Renderizado de métricas:
- `render_metrics()`: muestra KPIs en tarjetas
- Comparación base vs optimizado con deltas
- `render_best_params()`: destaca parámetros óptimos
- `render_optimization_results()`: tabla top 10 resultados

---

## 🎯 Cómo Usar

### Flujo básico:

1. **Abre la aplicación** con `streamlit run app.py`
2. **Selecciona un ticker** (ej: AAPL, BTC-USD)
3. **Define el período** de análisis
4. **Elige una estrategia** (RSI, SMA Crossover o MACD)
5. **Establece capital inicial** (default: $10,000)
6. **(Opcional) Activa optimización** para buscar mejores parámetros
7. **Presiona "Ejecutar análisis"**

### Interpretación de resultados:

**Tab 1 - Datos y Gráfica:**
- Gráfico de velas con indicadores superpuestos
- Últimas 10 barras con valores numéricos
- Información del período analizado

**Tab 2 - Backtesting:**
- Curva de capital (equity curve)
- Gráfico de puntos de entrada (triángulos verdes) y salida (triángulos rojos)
- Métricas principales
- Comparación base vs optimizado (si aplica)

**Tab 3 - Optimización:**
- Mejores parámetros encontrados
- Top 10 combinaciones por Sharpe Ratio
- Métricas de la optimización

---

## 📊 Métricas Explicadas

| Métrica | Descripción |
|---------|------------|
| **Retorno Total (%)** | Ganancia/pérdida total en porcentaje |
| **Sharpe Ratio** | Medida de riesgo-retorno ajustado (mayor = mejor) |
| **Drawdown Máximo (%)** | Pérdida máxima desde el pico anterior |
| **Win Rate (%)** | Porcentaje de operaciones ganadoras |
| **Operaciones** | Total de trades ejecutados |
| **Factor de Ganancias** | Ratio de ganancias brutas vs pérdidas brutas |
| **Duración Promedio** | Tiempo medio de cada posición abierta |
| **Exposición (%)** | Porcentaje de tiempo con posición abierta |

---

## ⚙️ Parámetros de Optimización

### RSI Strategy:
```
rsi_lower: 20-40 (paso 5)    # Umbral de compra
rsi_upper: 60-80 (paso 5)    # Umbral de venta
```

### SMA Crossover:
```
n_short: 5-20 (paso 2)       # Período SMA corta
n_long: 30-100 (paso 10)     # Período SMA larga
```

### MACD Strategy:
```
fast: 8-14 (paso 2)          # EMA rápida
slow: 24-30 (paso 2)         # EMA lenta
signal: 7-10 (paso 1)        # EMA señal
```

---

## 🔧 Stack Tecnológico

| Librería | Versión | Propósito |
|----------|---------|----------|
| **Streamlit** | 1.28.1 | Interfaz web interactiva |
| **Plotly** | 5.17.0 | Gráficos interactivos |
| **yfinance** | 0.2.32 | Descarga de datos históricos |
| **pandas** | 2.1.3 | Manipulación de datos |
| **numpy** | 1.26.2 | Cálculos numéricos |
| **pandas-ta** | 0.3.14b0 | Indicadores técnicos |
| **backtesting.py** | 0.3.3 | Motor de backtesting |

---

## 💡 Ejemplos de Uso

### Analizar AAPL con RSI:
1. Selecciona `AAPL` en el selector
2. Elige `RSI Strategy`
3. Presiona "Ejecutar análisis"

### Buscar mejores parámetros para Bitcoin:
1. Selecciona `BTC-USD`
2. Elige `SMA Crossover`
3. Activa "Optimización automática"
4. Presiona "Ejecutar análisis" (esperará 2-5 minutos)

### Comparar período corto vs largo:
- Ejecuta con rango corto (últimos 3 meses)
- Luego con rango largo (últimos 3 años)
- Compara las métricas en ambos backtests

---

## ⚠️ Disclaimer

Este es un **sistema educativo** diseñado para aprender sobre trading algorítmico y backtesting.

**No garantiza ganancia alguna** en mercados reales. El rendimiento pasado no es indicador del rendimiento futuro.

**Antes de operar en mercados reales:**
- Realiza tu propia investigación
- Comprende completamente cada estrategia
- Comienza con capital pequeño
- Gestiona el riesgo adecuadamente
- Consulta con un asesor financiero

---

## 🐛 Troubleshooting

### "Módulo no encontrado"
```
pip install -r requirements.txt
```

### "Ticker no válido"
Verifica que el ticker existe en Yahoo Finance (ej: AAPL, BTC-USD, ETH-USD)

### "No hay datos disponibles"
Aumenta el rango de fechas o intenta con otro activo

### La optimización es muy lenta
Reduce el rango de parámetros en `config/settings.py`

---

## 📝 Licencia

Este proyecto es de código abierto para propósitos educativos.

---

## 📧 Contacto y Soporte

Para reportar bugs o sugerencias, por favor crea un issue en el repositorio.

---

**¡Espero que disfrutes usando Trading Bot! 📈**
