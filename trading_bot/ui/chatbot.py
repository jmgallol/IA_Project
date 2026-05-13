# pyrefly: ignore [missing-import]
import streamlit as st

def render_chatbot(stats=None, ticker="el activo"):
    """Chatbot avanzado que analiza múltiples métricas de rendimiento."""
    st.sidebar.divider()
    st.sidebar.subheader(f"🤖 Analista IA: {ticker}")
    
    kb = {
        "sharpe": "El Sharpe Ratio mide el retorno vs riesgo. >1 es bueno, >2 es excelente.",
        "drawdown": "Es la caída máxima que sufrió tu dinero. Si es muy alta (>25%), podrías perder los nervios y cerrar la cuenta.",
        "win rate": "Porcentaje de aciertos. Un 60% es muy bueno en trading.",
        "profit factor": "Si es 2.0, significa que ganas $2 por cada $1 que pierdes. ¡Eso es genial!",
        "optimizacion": "La IA prueba miles de combinaciones para que tú no tengas que adivinar los mejores parámetros.",
        "rsi": "Mide si la gente está comprando demasiado (caro) o vendiendo demasiado (barato).",
        "macd": "Detecta cuándo el precio empieza a subir o bajar con fuerza (tendencia)."
    }

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"¡Hola! Soy tu analista. Ejecuta el análisis y pregúntame: '¿Cómo fue mi desempeño?' para darte un reporte completo."}]

    chat_container = st.sidebar.container(height=380)
    
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.sidebar.chat_input("Escribe aquí...", key="chat_input_v4"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        p_low = prompt.lower()
        response = "Puedes preguntarme por: Sharpe, Profit Factor, Win Rate o mi opinión sobre tus resultados."

        if stats is not None and any(word in p_low for word in ["resultados", "fue", "analisis", "opinion", "desempeño"]):
            retorno = stats['Return [%]']
            mercado = stats['Buy & Hold Return [%]']
            sharpe = stats['Sharpe Ratio']
            win_rate = stats['Win Rate [%]']
            profit_factor = stats['Profit Factor']
            dd = stats['Max. Drawdown [%]']
            
            # Análisis por niveles
            res_ret = "¡Ganaste al mercado!" if retorno > mercado else "El mercado (comprar y mantener) fue mejor esta vez."
            res_win = "Tienes un buen porcentaje de acierto." if win_rate > 50 else "Aciertas pocas veces, pero quizás las que ganas son muy grandes."
            res_pf = "Tu estrategia es muy rentable por cada dólar arriesgado." if profit_factor > 1.5 else "Tu rentabilidad por riesgo es ajustada."
            res_dd = "Además, el riesgo (drawdown) fue controlado." if abs(dd) < 15 else "Pero ojo, tuviste caídas de capital fuertes (riesgo alto)."
            
            response = f"**Reporte para {ticker}:**\n\n1. {res_ret} ({retorno:.1f}% vs {mercado:.1f}%).\n2. {res_win} (Win Rate: {win_rate:.1f}%).\n3. {res_pf} (Profit Factor: {profit_factor:.2f}).\n4. {res_dd} (Máxima caída: {dd:.1f}%)."
        
        else:
            for key, value in kb.items():
                if key in p_low:
                    response = value
                    break
            
            if any(word in p_low for word in ["hola", "buenos", "que tal"]):
                response = f"¡Hola! Haz clic en 'Ejecutar análisis' y luego pregúntame cómo fue tu desempeño con {ticker}."

        st.session_state.messages.append({"role": "assistant", "content": response})
        with chat_container.chat_message("assistant"):
            st.markdown(response)
