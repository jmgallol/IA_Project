# 📈 Trading Bot - Sistema Algorítmico de Trading

Un sistema completo de **trading algorítmico** con **backtesting automático** y **optimización de parámetros** desarrollado en Python con interfaz interactiva en Streamlit.

## 🎯 Características

- ✅ **3 Estrategias de Trading predefinidas**: RSI, SMA Crossover, MACD
- ✅ **Backtesting realista** con comisiones e indicadores técnicos
- ✅ **Optimización automática** de parámetros usando grid search
- ✅ **Visualizaciones interactivas** con Plotly
- ✅ **Interfaz intuitiva** en Streamlit
- ✅ **Análisis de más de 8000+ activos** (acciones, criptomonedas, ETFs)
- ✅ **Métricas avanzadas**: Sharpe Ratio, Drawdown, Win Rate, etc.

## 🔧 Stack Tecnológico

| Librería | Propósito |
|----------|-----------|
| **yfinance** | Descarga de datos históricos |
| **pandas & numpy** | Procesamiento de datos |
| **backtesting.py** | Motor de backtesting |
| **Plotly** | Visualizaciones interactivas |
| **Streamlit** | Interfaz web |
| **pandas-ta** | Indicadores técnicos |

## 📁 Estructura del Proyecto

```
trading_bot/
├── app.py                  # Punto de entrada principal (Streamlit)
├── config/
│   └── settings.py         # Constantes y configuración global
├── data/
│   └── loader.py           # Descarga y limpieza de datos
├── indicators/
│   └── technical.py        # Cálculo de indicadores técnicos
├── strategies/
│   ├── rsi_strategy.py     # Estrategia basada en RSI
│   ├── sma_strategy.py     # Estrategia de cruce de medias móviles
│   └── macd_strategy.py    # Estrategia basada en MACD
├── backtest/
│   ├── engine.py           # Lógica del backtesting
│   └── optimizer.py        # Optimización de parámetros
├── ui/
│   ├── sidebar.py          # Panel lateral de Streamlit
│   ├── charts.py           # Gráficas con Plotly
│   └── metrics.py          # Visualización de métricas
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Este archivo
```

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.10+
- pip (gestor de paquetes de Python)

### Paso 1: Instalar Dependencias
```bash
pip install -r requirements.txt
```

> **Nota**: La primera instalación puede tomar 2-3 minutos descargando e instalando todas las librerías.

### Paso 2: Ejecutar la Aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador por defecto en `http://localhost:8501`

## 📖 Guía de Uso

### 1️⃣ Configuración Inicial
En el **panel lateral izquierdo** podrás:
- Seleccionar un **ticker** (ej: AAPL, BTC-USD, SPY)
- Definir el **rango de fechas** para el análisis
- Elegir la **estrategia de trading**
- Configurar el **capital inicial** (1,000 - 100,000 USD)

### 2️⃣ Ejecutar el Análisis
Haz clic en el botón **"🚀 Ejecutar análisis"**

El bot ejecutará en orden:
1. Descarga de datos históricos
2. Cálculo de indicadores técnicos
3. Backtesting con parámetros por defecto
4. Optimización de parámetros (si está activada)

### 3️⃣ Interpretar los Resultados

#### Tab 1: 📊 Datos y Gráfica
- Gráfico de velas con indicadores superpuestos
- SMA 20 y SMA 50
- Bandas de Bollinger
- Volumen

#### Tab 2: 📈 Backtesting
- Métricas de desempeño (Retorno, Sharpe, Drawdown, etc.)
- Curva de capital (Equity Curve)
- Puntos de entrada y salida

#### Tab 3: 🏆 Optimización
- Mejores parámetros encontrados
- Comparación con parámetros por defecto
- Top 10 combinaciones de parámetros

## 📊 Estrategias Disponibles

### 1. RSI Strategy (Relative Strength Index)
**Lógica:**
- **Compra** cuando RSI < 30 (sobreventa)
- **Vende** cuando RSI > 70 (sobrecompra)

**Parámetros optimizables:**
- `rsi_lower`: 20-40
- `rsi_upper`: 60-80

### 2. SMA Crossover (Cruce de Medias Móviles)
**Lógica:**
- **Compra** en cruce alcista (SMA corta > SMA larga)
- **Vende** en cruce bajista (SMA corta < SMA larga)

**Parámetros optimizables:**
- `n_short`: 5-20 periodos
- `n_long`: 30-100 periodos

### 3. MACD Strategy (Moving Average Convergence Divergence)
**Lógica:**
- **Compra** cuando MACD cruza hacia arriba la línea de señal
- **Vende** cuando MACD cruza hacia abajo la línea de señal

**Parámetros fijos:**
- MACD: 12/26/9

## 📈 Indicadores Técnicos Utilizados

| Indicador | Período | Uso |
|-----------|---------|-----|
| RSI | 14 | Detectar sobreventa/sobrecompra |
| SMA | 20, 50 | Identificar tendencias |
| EMA | 12, 26 | Componentes del MACD |
| MACD | 12/26/9 | Señales de momentum |
| Bandas Bollinger | 20, ±2σ | Volatilidad |

## 🎓 Métricas Explicadas

| Métrica | Descripción | Ideal |
|---------|-------------|-------|
| **Retorno (%)** | Ganancia/pérdida total | > 0% |
| **Sharpe Ratio** | Retorno ajustado por riesgo | > 1.0 |
| **Drawdown Máx.** | Máxima pérdida desde pico | Cercano a 0% |
| **Win Rate (%)** | % de operaciones ganadoras | > 50% |
| **Profit Factor** | Ganancias brutas / Pérdidas | > 1.5 |
| **Exposición (%)** | % de tiempo con posición abierta | > 30% |

## ⚙️ Configuración Avanzada

### Personalizar Parámetros de Optimización
Edita `config/settings.py`:

```python
# Ejemplo: Cambiar rangos de RSI
RSI_PARAMS = {
    'rsi_lower': range(15, 51, 5),   # 15-50
    'rsi_upper': range(50, 91, 5)    # 50-90
}
```

### Cambiar Capital Inicial por Defecto
```python
CAPITAL_INICIAL_DEFAULT = 20000  # Cambiar de 10,000 a 20,000
```

### Modificar Comisión
Edita `backtest/engine.py`:
```python
commission=0.002  # Cambiar de 0.1% a 0.2%
```

## 📊 Ejemplos de Uso

### Ejemplo 1: Backtesting del S&P 500
1. Ticker: `SPY`
2. Período: Últimos 2 años
3. Estrategia: `SMA Crossover`
4. Capital: $10,000
5. Optimización: Desactivada

### Ejemplo 2: Optimización de Bitcoin
1. Ticker: `BTC-USD`
2. Período: Últimos 3 años
3. Estrategia: `RSI Strategy`
4. Capital: $5,000
5. Optimización: Activada ✓

## ⚠️ Disclaimers Importantes

- 🔴 **El backtesting no garantiza desempeño futuro**
- 🔴 **No utilices este bot con dinero real sin validación adecuada**
- 🔴 **Las estrategias pueden no funcionar en condiciones de mercado extremas**
- 🔴 **Realiza tu propia investigación y análisis antes de operar**

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named..."
```bash
pip install --upgrade -r requirements.txt
```

### "ConnectionError: No data available"
- Verifica que el ticker sea válido (ej: AAPL, BTC-USD)
- Comprueba tu conexión a internet
- Algunos tickers de criptomonedas requieren sufijo `-USD`

### "Optimization takes too long"
- Reduce el rango de parámetros en `config/settings.py`
- Usa un período más corto (ej: últimos 6 meses)

### Streamlit not found
```bash
pip install streamlit --upgrade
```

## 📚 Recursos Adicionales

- [Documentación de backtesting.py](https://kernc.github.io/backtesting.py/)
- [Guía de Streamlit](https://docs.streamlit.io/)
- [yfinance en GitHub](https://github.com/ranaroussi/yfinance)
- [Análisis Técnico - Investopedia](https://www.investopedia.com/terms/t/technical-analysis.asp)

## 💡 Ideas de Mejora Futura

- [ ] Agregar más estrategias (Bollinger Bands, Stochastic, etc.)
- [ ] Implementar machine learning para predicción
- [ ] Exportar reportes en PDF
- [ ] Dashboard con histórico de backtests
- [ ] Integración con brokers reales (Paper Trading)
- [ ] Alertas automáticas por email
- [ ] API REST para acceso programático

## 📝 Licencia

Este proyecto es de código abierto. Úsalo libremente para fines educativos.

## 👨‍💻 Desarrollador

**Trading Bot v1.0** - Sistema algorítmico de backtesting
Desarrollado con ❤️ en Python

---

### 🎉 ¡Listo para tradear!

Ejecuta `streamlit run app.py` y comienza tu análisis de trading algorítmico ahora.

**¿Preguntas o sugerencias?** Abre un issue o contacta al desarrollador.
