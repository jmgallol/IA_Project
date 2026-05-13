# pyrefly: ignore [missing-import]
import json
import os

import streamlit as st

GEMINI_MODEL = "gemini-2.5-flash-lite"


SYSTEM_PROMPT = """
Eres un asistente educativo para una app academica de backtesting de estrategias de trading.

Reglas obligatorias:
- Responde solo usando el CONTEXTO_ANALISIS entregado por la aplicacion.
- Si el contexto no contiene un dato, dilo claramente. No inventes metricas, fechas, precios ni parametros.
- No recomiendes comprar, vender, holdear ni invertir dinero real.
- Usa frases como "segun los resultados historicos", "en el periodo evaluado" y "no garantiza resultados futuros".
- Interpreta los resultados como hipotesis de analisis, no como recomendacion de inversion.
- Explica en espanol claro, con respuestas breves y utiles para una demo academica.
- Si el usuario pide consejo financiero real, rechaza suavemente y vuelve al analisis historico.
"""


def render_chatbot(stats=None, ticker="el activo", comparison=None):
    """Renderiza un asistente LLM con fallback local."""
    st.sidebar.divider()
    st.sidebar.subheader(f"Analista IA: {ticker}")

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

        context = build_analysis_context(stats=stats, ticker=ticker, comparison=comparison)
        response = generate_response(prompt, context)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with chat_container.chat_message("assistant"):
            st.markdown(response)


def generate_response(prompt, context):
    """Intenta responder con Gemini y usa fallback local si no esta disponible."""
    fallback = build_fallback_response(prompt, context)
    api_key = get_gemini_api_key()
    if not api_key:
        return (
            f"{fallback}\n\n"
            "_Nota: Gemini no esta configurado. Agrega `GEMINI_API_KEY` en "
            "`.streamlit/secrets.toml` para activar respuestas con LLM._"
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return (
            f"{fallback}\n\n"
            "_Nota: falta instalar `google-genai`. Ejecuta `pip install -r requirements.txt`._"
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=build_user_prompt(prompt, context),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
            ),
        )
    except Exception as error:
        return (
            f"{fallback}\n\n"
            f"_Nota: no fue posible consultar Gemini ({error}). Se uso respuesta local._"
        )

    text = getattr(response, "text", None)
    if not text:
        return fallback

    return text


def get_gemini_api_key():
    """Lee la API key sin guardarla en codigo."""
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        secret_key = None

    return secret_key or os.getenv("GEMINI_API_KEY")


def build_user_prompt(prompt, context):
    return (
        "CONTEXTO_ANALISIS:\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        "PREGUNTA_USUARIO:\n"
        f"{prompt}\n\n"
        "Responde usando unicamente el CONTEXTO_ANALISIS."
    )


def build_analysis_context(stats=None, ticker="el activo", comparison=None):
    """Construye un contexto pequeno y estructurado para Gemini."""
    if comparison is not None:
        return {
            "mode": "strategy_comparison",
            "ticker": ticker,
            "comparison": comparison,
            "allowed_conclusions": [
                "comparar retorno historico",
                "comparar drawdown historico",
                "comparar Sharpe Ratio historico",
                "comparar contra Buy & Hold",
                "identificar estrategia mas equilibrada segun el score calculado",
            ],
            "disclaimer": "No es recomendacion de inversion y no garantiza resultados futuros.",
        }

    if stats is not None:
        return {
            "mode": "single_strategy",
            "ticker": ticker,
            "metrics": {
                "return_pct": safe_stat(stats, "Return [%]"),
                "buy_hold_return_pct": safe_stat(stats, "Buy & Hold Return [%]"),
                "sharpe_ratio": safe_stat(stats, "Sharpe Ratio"),
                "max_drawdown_pct": safe_stat(stats, "Max. Drawdown [%]"),
                "win_rate_pct": safe_stat(stats, "Win Rate [%]"),
                "profit_factor": safe_stat(stats, "Profit Factor"),
                "trades": safe_stat(stats, "# Trades"),
                "final_equity": safe_stat(stats, "Equity Final [$]"),
            },
            "disclaimer": "No es recomendacion de inversion y no garantiza resultados futuros.",
        }

    return {
        "mode": "no_analysis",
        "ticker": ticker,
        "message": "Todavia no hay resultados calculados en la aplicacion.",
    }


def build_fallback_response(prompt, context):
    """Respuesta local acotada cuando Gemini no esta disponible."""
    p_low = prompt.lower()

    if context["mode"] == "strategy_comparison":
        return build_comparison_fallback(p_low, context["comparison"])

    if context["mode"] == "single_strategy":
        return build_single_strategy_fallback(p_low, context)

    return "Ejecuta primero un analisis para que pueda interpretar resultados historicos."


def build_single_strategy_fallback(prompt, context):
    metrics = context["metrics"]

    if any(word in prompt for word in ["resultado", "desempeno", "desempeño", "opinion", "analisis"]):
        relation = (
            "supero a Buy & Hold"
            if metrics["return_pct"] > metrics["buy_hold_return_pct"]
            else "no supero a Buy & Hold"
        )
        return (
            f"Segun los resultados historicos, la estrategia {relation}: "
            f"{metrics['return_pct']:.2f}% vs Buy & Hold {metrics['buy_hold_return_pct']:.2f}%. "
            f"Sharpe: {metrics['sharpe_ratio']:.2f}, drawdown maximo: "
            f"{metrics['max_drawdown_pct']:.2f}%, operaciones: {metrics['trades']:.0f}. "
            "No garantiza resultados futuros."
        )

    if "sharpe" in prompt:
        return (
            f"Segun los resultados historicos, el Sharpe Ratio fue "
            f"{metrics['sharpe_ratio']:.2f}. Este valor resume retorno ajustado por volatilidad."
        )

    if "drawdown" in prompt:
        return (
            f"En el periodo evaluado, el drawdown maximo fue "
            f"{metrics['max_drawdown_pct']:.2f}%. Representa la peor caida historica de capital."
        )

    return (
        "Puedo interpretar retorno, Sharpe Ratio, drawdown, Win Rate, Profit Factor "
        "o comparar contra Buy & Hold usando los resultados historicos."
    )


def build_comparison_fallback(prompt, comparison):
    winners = comparison["winners"]
    rows = comparison["rows"]
    buy_hold = comparison["buy_hold"]

    if any(word in prompt for word in ["rentable", "mayor retorno", "mas retorno", "más retorno"]):
        row = find_row(rows, winners["highest_return"])
        return historical_response(
            f"la estrategia mas rentable fue **{row['strategy']}**, con retorno de "
            f"{row['return_pct']:.2f}% y capital final de ${row['final_equity']:,.2f}."
        )

    if any(word in prompt for word in ["menos riesgosa", "menor riesgo", "menor drawdown", "menos riesgo"]):
        row = find_row(rows, winners["lowest_drawdown"])
        return historical_response(
            f"la estrategia con menor drawdown fue **{row['strategy']}**, con "
            f"{row['max_drawdown_pct']:.2f}%."
        )

    if any(word in prompt for word in ["mejor sharpe", "rentabilidad/riesgo", "relacion", "riesgo"]):
        row = find_row(rows, winners["best_sharpe"])
        return historical_response(
            f"la mejor relacion retorno/riesgo por Sharpe fue **{row['strategy']}**, "
            f"con Sharpe Ratio de {row['sharpe_ratio']:.2f}."
        )

    if any(word in prompt for word in ["equilibrada", "balanceada", "score"]):
        row = find_row(rows, winners["balanced"])
        return historical_response(
            f"la estrategia mas equilibrada fue **{row['strategy']}**, con score "
            f"{row['balanced_score']:.2f}."
        )

    if "buy" in prompt or "hold" in prompt or "supero" in prompt or "superó" in prompt:
        beaters = [row["strategy"] for row in rows if row["beats_buy_hold"]]
        if beaters:
            return historical_response(
                f"las estrategias que superaron a Buy & Hold fueron: **{', '.join(beaters)}**. "
                f"Buy & Hold tuvo retorno de {buy_hold['return_pct']:.2f}%."
            )

        return historical_response(
            f"ninguna estrategia supero a Buy & Hold. Buy & Hold tuvo retorno de "
            f"{buy_hold['return_pct']:.2f}%."
        )

    return historical_response(
        f"mayor retorno: **{winners['highest_return']}**; menor drawdown: "
        f"**{winners['lowest_drawdown']}**; mejor Sharpe: **{winners['best_sharpe']}**; "
        f"mas equilibrada: **{winners['balanced']}**."
    )


def safe_stat(stats, key, default=0.0):
    try:
        value = float(stats[key])
    except Exception:
        return default

    if value != value or value in (float("inf"), float("-inf")):
        return default

    return value


def find_row(rows, strategy_name):
    for row in rows:
        if row["strategy"] == strategy_name:
            return row

    return rows[0]


def historical_response(message):
    return (
        f"Segun los resultados historicos, {message} "
        "En el periodo evaluado esto no garantiza resultados futuros y debe interpretarse "
        "como una hipotesis de analisis, no como recomendacion de inversion."
    )

