# Guion y Estructura de Presentación - Trading Bot (20 Minutos)

**Recomendación de Diapositivas:** Usa un diseño limpio. Menos texto, más gráficos. Las capturas de la aplicación o esquemas visuales mantienen la atención.

---

## 👤 PERSONA 1: Introducción, Contexto y Propuesta de Valor (Aprox. 3-4 min)
*Esta persona debe hablar con mucha seguridad para "enganchar" al jurado/profesor.*

**Diapositiva 1: Título y Presentación del Equipo**
*   "Buenos días/tardes. Somos [Nombres] y hoy presentamos nuestro proyecto final de Inteligencia Artificial: Un sistema automatizado para la evaluación y optimización de estrategias de Trading Cuantitativo."

**Diapositiva 2: El Problema**
*   **¿Qué dices?:** Todo el tiempo escuchamos sobre invertir en la bolsa o criptomonedas, pero la realidad es que el 90% de los inversores minoristas pierden dinero. ¿Por qué? Porque operan guiados por la emoción, rumores o "análisis visual" subjetivo viendo gráficos. No prueban matemáticamente si sus ideas funcionan antes de arriesgar su dinero.

**Diapositiva 3: Nuestra Propuesta de Valor (El Estado del Arte vs Nuestro Aporte)**
*   **¿Qué dices?:** Existen varias soluciones en la industria, pero todas tienen barreras de entrada:
    1.  **Terminales como Bloomberg o Interactive Brokers:** Son para instituciones, cuestan miles de dólares y requieren experiencia avanzada. *Nuestro aporte:* Democratizamos el acceso construyendo un simulador gratuito para estudiantes.
    2.  **Librerías Puras (Backtrader/VectorBT):** Requieren saber programar avanzado. *Nuestro aporte:* Una interfaz visual intuitiva (no code). Todo se maneja con clics y sliders.
    3.  **Análisis Manual vs Algorítmico:** En vez de que un trader pase horas dibujando líneas guiado por sus emociones, nuestro sistema genera reportes objetivos.
    4.  **Machine Learning Puro (Cajas Negras):** Las redes neuronales predicen, pero no sabemos *por qué*. *Nuestro aporte:* Nosotros creamos un sistema basado en "Reglas Interpretables" y matemáticas (ej. RSI, Medias Móviles), donde cualquiera puede auditar y entender *por qué* el bot compró o vendió.

---

## 👤 PERSONA 2: Arquitectura y Metodología (Aprox. 4 min)
*Esta persona explica el "cómo lo hicimos", el motor técnico del proyecto.*

**Diapositiva 4: Arquitectura del Sistema (Mostrar diagrama de bloques o el Mermaid del README)**
*   **¿Qué dices?:** Desarrollamos el sistema con una arquitectura modular en Python. Usamos:
    *   `yfinance` para descargar en tiempo real datos de más de 8,000 activos.
    *   `pandas` para el cálculo vectorizado de indicadores técnicos.
    *   `backtesting.py` como motor principal de simulación (que tiene en cuenta comisiones realistas del 0.1%).
    *   `Streamlit` y `Plotly` para empaquetar todo en una aplicación web interactiva.

**Diapositiva 5: Las Estrategias y el Motor Analítico**
*   **¿Qué dices?:** En el núcleo de nuestro bot evaluamos 3 familias clásicas de estrategias:
    1.  **RSI (Relative Strength Index):** Busca activos "sobrevendidos" para comprar barato.
    2.  **SMA Crossover:** Usa el cruce de medias móviles para identificar cambios de tendencia.
    3.  **MACD:** Estrategia basada en el *momentum* del mercado.
    *   Además, integramos un **Grid Search Optimizador** interno, un algoritmo de fuerza bruta que evalúa cientos de variaciones de una misma estrategia para encontrar la combinación matemáticamente perfecta basada en la métrica *Sharpe Ratio*.

---

## 👤 PERSONA 3: Demo en Vivo - Ejecución Básica (Aprox. 5 min)
*La demostración en vivo es crucial. Ten la app abierta en `http://localhost:8501/` antes de empezar.*

**Parte Práctica (Compartiendo pantalla en la App)**
1.  **Explicar la Interfaz:** "Esta es nuestra plataforma. Como ven a la izquierda, el usuario no toca código. Elegimos un activo, digamos AAPL (Apple), y definimos fechas de los últimos 3 años con 10,000 dólares iniciales."
2.  **Tab 1 - Datos y Gráficos:** Selecciona la estrategia RSI y dale a ejecutar. 
    *   *Comenta:* "Automáticamente el sistema descarga la data y calcula indicadores pesados. Aquí vemos las Bandas de Bollinger, medias móviles y el volumen. Es un análisis visual completo."
3.  **Tab 2 - Backtesting:** 
    *   *Comenta:* "Pero la magia real pasa aquí. Nuestro motor simuló qué habría pasado si operábamos Apple con RSI (30,70) durante estos 3 años."
    *   Muestra la curva de capital azul contra el "Buy & Hold" naranja.
    *   Destaca métricas clave: "Miren el **Sharpe Ratio** (que mide retorno vs riesgo) y el **Drawdown Máximo** (nuestra peor caída posible)." 
    *   Muestra los triángulos de colores en la gráfica inferior: "El sistema documenta de forma transparente los puntos exactos de entrada (verde) y salida (rojo)."

---

## 👤 PERSONA 4: Demo - Optimización, Resultados y Conclusiones (Aprox. 7-8 min)
*Cierra con fuerza demostrando la inteligencia del algoritmo de optimización y dando conclusiones realistas.*

**Parte Práctica (Compartiendo pantalla en la App)**
1.  **Tab 3 - Optimización:**
    *   *Comenta:* "¿Pero qué pasa si RSI 30/70 no es lo óptimo para Apple? Aquí entra nuestro Grid Search".
    *   Activa la casilla "Optimizar Parámetros de Estrategia" y dale click.
    *   Mientras carga, explica: "El algoritmo ahora está probando decenas de combinaciones matemáticas para encontrar la mejor. Y aquí está el resultado."
    *   Muestra la tabla de las mejores combinaciones. "Vemos que para Apple, quizás un RSI de 35 y 75 era mucho más seguro."

**Diapositiva 6: Resultados Principales (Retornando al PowerPoint)**
*   **¿Qué dices?:** Evaluando nuestra aplicación de manera rigurosa, encontramos lo siguiente: *(Puedes usar los datos de la tabla "Resultados" del README)*
    *   Ninguna estrategia de Análisis Técnico básico funciona para todos los activos por igual; el mercado es muy dinámico.
    *   El "Buy & Hold" (comprar y guardar) en empresas sólidas de alto crecimiento suele ganarle al trading activo en mercados alcistas, confirmando varias teorías financieras.
    *   Sin embargo, nuestra herramienta demostró que las estrategias activas reducen sustancialmente las pérdidas severas (Drawdown) en comparación con simplemente quedarse comprado durante caídas fuertes del mercado.

**Diapositiva 7: Conclusiones y Trabajo Futuro**
*   **¿Qué dices?:** Para concluir, hemos logrado construir un ecosistema completo para la evaluación financiera cuantitativa, democratizando herramientas que antes eran inaccesibles para el usuario promedio.
    *   **Limitaciones (Autocrítica):** Sabemos que el backtesting no es perfecto, porque rendimientos pasados no garantizan rendimientos futuros y existen desviaciones como el 'slippage'.
    *   **Trabajo Futuro:** El sistema está preparado para escalar. El siguiente paso natural sería agregar modelos de predicción estocásticos o conectarlo a una API de un Broker real para hacer simulaciones en vivo.

*   "Muchas gracias por su atención. Estamos abiertos a responder cualquier duda o realizar pruebas en vivo si lo desean."
