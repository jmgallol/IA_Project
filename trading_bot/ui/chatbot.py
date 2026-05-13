# pyrefly: ignore [missing-import]
import streamlit as st


def render_chatbot(stats=None, ticker="el activo", comparison=None):
    """Renderiza un asistente simple basado en resultados historicos."""
    st.sidebar.divider()
    st.sidebar.subheader(f"Analista IA: {ticker}")

    kb = {
        "sharpe": "El Sharpe Ratio mide retorno ajustado por volatilidad. Un valor mayor indica mejor relacion retorno/riesgo, pero debe revisarse junto con drawdown y operaciones.",
        "drawdown": "El drawdown maximo es la peor caida del capital desde un pico hasta un minimo posterior.",
        "win rate": "Win Rate es el porcentaje de operaciones ganadoras. No basta por si solo: tambien importa cuanto se gana y cuanto se pierde.",
        "profit factor": "Profit Factor compara ganancias brutas contra perdidas brutas. Puede salir NaN si hay pocas operaciones o no hay perdidas realizadas.",
        "optimizacion": "La optimizacion prueba combinaciones de parametros y elige la mejor segun la funcion objetivo seleccionada.",
        "rsi": "RSI se asocia a reversion a la media: busca posibles zonas de sobrecompra o sobreventa.",
        "macd": "MACD intenta detectar cambios de tendencia o momentum mediante medias exponenciales.",
        "sma": "SMA Crossover usa cruces de medias moviles para seguir posibles tendencias.",
    }

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hola. Ejecuta un analisis y preguntame por resultados, "
                    "Buy & Hold o comparacion de estrategias."
                ),
            }
        ]

    chat_container = st.sidebar.container(height=380)

    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.sidebar.chat_input("Escribe aqui...", key="chat_input_v4"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        response = build_response(prompt, stats=stats, ticker=ticker, comparison=comparison, kb=kb)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with chat_container.chat_message("assistant"):
            st.markdown(response)


def build_response(prompt, stats=None, ticker="el activo", comparison=None, kb=None):
    """Construye respuestas acotadas a los datos historicos disponibles."""
    p_low = prompt.lower()
    kb = kb or {}

    if comparison is not None:
        comparative_response = build_comparison_response(p_low, comparison)
        if comparative_response is not None:
            return comparative_response

    if stats is not None and any(
        word in p_low for word in ["resultados", "fue", "analisis", "opinion", "desempeno", "desempeño"]
    ):
        retorno = stats["Return [%]"]
        mercado = stats["Buy & Hold Return [%]"]
        win_rate = stats["Win Rate [%]"]
        profit_factor = stats["Profit Factor"]
        dd = stats["Max. Drawdown [%]"]

        res_ret = (
            "supero a Buy & Hold"
            if retorno > mercado
            else "no supero a Buy & Hold"
        )
        res_win = (
            "tuvo un porcentaje de acierto alto"
            if win_rate > 50
            else "tuvo un porcentaje de acierto bajo o moderado"
        )
        res_pf = (
            "mostro buena relacion entre ganancias y perdidas"
            if profit_factor > 1.5
            else "tuvo una relacion ganancia/perdida ajustada o poco concluyente"
        )
        res_dd = (
            "el drawdown fue relativamente controlado"
            if abs(dd) < 15
            else "el drawdown fue alto y debe revisarse con cuidado"
        )

        return (
            f"Segun los resultados historicos para **{ticker}**, la estrategia {res_ret} "
            f"({retorno:.1f}% vs {mercado:.1f}%). Ademas, {res_win} "
            f"(Win Rate: {win_rate:.1f}%), {res_pf} (Profit Factor: {profit_factor:.2f}) "
            f"y {res_dd} (Max Drawdown: {dd:.1f}%). "
            "Esto no garantiza resultados futuros y no debe interpretarse como recomendacion de inversion."
        )

    for key, value in kb.items():
        if key in p_low:
            return value

    if any(word in p_low for word in ["hola", "buenos", "que tal"]):
        return (
            f"Hola. Ejecuta el analisis de {ticker} y puedo ayudarte a interpretar "
            "metricas o comparar estrategias."
        )

    return (
        "Puedes preguntarme por Sharpe, drawdown, Profit Factor, Win Rate, "
        "Buy & Hold o por la comparacion de estrategias."
    )


def build_comparison_response(prompt, comparison):
    winners = comparison["winners"]
    rows = comparison["rows"]
    buy_hold = comparison["buy_hold"]

    if any(word in prompt for word in ["rentable", "mayor retorno", "mas retorno", "más retorno"]):
        row = _find_row(rows, winners["highest_return"])
        return _historical_response(
            f"La estrategia mas rentable fue **{row['strategy']}**, con retorno de "
            f"{row['return_pct']:.2f}% y capital final de ${row['final_equity']:,.2f}."
        )

    if any(word in prompt for word in ["menos riesgosa", "menor riesgo", "menor drawdown", "menos riesgo"]):
        row = _find_row(rows, winners["lowest_drawdown"])
        return _historical_response(
            f"La estrategia con menor drawdown fue **{row['strategy']}**, con drawdown maximo de "
            f"{row['max_drawdown_pct']:.2f}%."
        )

    if any(word in prompt for word in ["mejor sharpe", "rentabilidad/riesgo", "relacion", "riesgo"]):
        row = _find_row(rows, winners["best_sharpe"])
        return _historical_response(
            f"La mejor relacion retorno/riesgo por Sharpe fue **{row['strategy']}**, "
            f"con Sharpe Ratio de {row['sharpe_ratio']:.2f}."
        )

    if any(word in prompt for word in ["equilibrada", "balanceada", "score"]):
        row = _find_row(rows, winners["balanced"])
        return _historical_response(
            f"La estrategia mas equilibrada fue **{row['strategy']}**, usando el score "
            f"Sharpe - abs(drawdown) * 0.5. Su score fue {row['balanced_score']:.2f}."
        )

    if "buy" in prompt or "hold" in prompt or "supero" in prompt or "superó" in prompt:
        beaters = [row["strategy"] for row in rows if row["beats_buy_hold"]]
        if beaters:
            strategies = ", ".join(beaters)
            return _historical_response(
                f"Las estrategias que superaron a Buy & Hold fueron: **{strategies}**. "
                f"Buy & Hold tuvo retorno de {buy_hold['return_pct']:.2f}%."
            )

        return _historical_response(
            f"Ninguna estrategia supero a Buy & Hold en retorno total. "
            f"Buy & Hold tuvo retorno de {buy_hold['return_pct']:.2f}%."
        )

    if any(word in prompt for word in ["futuro", "considerar", "razonable"]):
        row = _find_row(rows, winners["balanced"])
        return _historical_response(
            f"Para analisis futuro seria razonable estudiar **{row['strategy']}** porque fue la mas equilibrada "
            "en el periodo evaluado. Esto es una hipotesis de analisis, no una recomendacion de inversion."
        )

    if any(word in prompt for word in ["comparacion", "comparar", "estrategia"]):
        return _historical_response(
            f"Mayor retorno: **{winners['highest_return']}**. "
            f"Menor drawdown: **{winners['lowest_drawdown']}**. "
            f"Mejor Sharpe: **{winners['best_sharpe']}**. "
            f"Mas equilibrada: **{winners['balanced']}**."
        )

    return None


def _find_row(rows, strategy_name):
    for row in rows:
        if row["strategy"] == strategy_name:
            return row

    return rows[0]


def _historical_response(message):
    return (
        f"Segun los resultados historicos, {message} "
        "En el periodo evaluado esto no garantiza resultados futuros y debe interpretarse "
        "como una hipotesis de analisis, no como recomendacion de inversion."
    )

