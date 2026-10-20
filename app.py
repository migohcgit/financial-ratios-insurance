
from pathlib import Path
import tempfile
import os

import pandas as pd
import streamlit as st

from src.orchestrator.caller import analyze_file


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Insurance Financial Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Análisis financiero de seguros")
st.write(
    "Análisis financiero e informes para compañías de seguros."
)

st.sidebar.title("Navegación")

section = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "Salpicadero",
        "Estados financieros",
        "Ratios financieros",
        "Interpretación",
    ],
)


# ==========================================
# ESTADO DE LA APLICACIÓN
# ==========================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

result = st.session_state.analysis_result


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

RATIO_NAMES = {
    "current_ratio": "Razón circulante",
    "cash_ratio": "Razón de efectivo",
    "debt_to_assets": "Pasivo / Activos",
    "equity_ratio": "Capital / Activos",
    "net_profit_margin": "Margen de utilidad neta",
    "return_on_assets": "Rendimiento sobre activos (ROA)",
    "return_on_equity": "Rendimiento sobre capital (ROE)",
    "claims_ratio": "Ratio de siniestralidad",
    "expense_ratio": "Ratio de gastos",
    "combined_ratio": "Ratio combinado",
    "investment_yield": "Rendimiento de inversiones",
}

PERCENTAGE_RATIOS = {
    "debt_to_assets",
    "equity_ratio",
    "net_profit_margin",
    "return_on_assets",
    "return_on_equity",
    "claims_ratio",
    "expense_ratio",
    "combined_ratio",
    "investment_yield",
}


def format_ratio(name, value):
    if value is None:
        return "No calculable"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if name in PERCENTAGE_RATIOS:
        return f"{number:.2%}"

    return f"{number:.3f}"


def get_ratios(analysis):
    return getattr(analysis, "ratios", None) or []


def get_issues(analysis):
    return getattr(analysis, "issues", None) or []


def ratio_table(analysis):
    rows = []

    for ratio in get_ratios(analysis):
        rows.append({
            "Indicador": RATIO_NAMES.get(
                ratio.name, ratio.name.replace("_", " ").title()
            ),
            "Resultado": format_ratio(ratio.name, ratio.value),
            "Estado": ratio.status,
            "Fórmula": ratio.formula,
            "Interpretación": getattr(
                ratio, "interpretation", None
            ) or "Sin interpretación disponible",
        })

    return pd.DataFrame(rows)


# ==========================================
# 1. SALPICADERO
# ==========================================

if section == "Salpicadero":
    st.header("Panel de control financiero")

    if result is None:
        st.info(
            "¡Bienvenido! Sube un estado financiero "
            "para comenzar el análisis."
        )
    else:
        ratios = get_ratios(result)
        issues = get_issues(result)
        data = getattr(result, "normalized_data", None) or {}

        col1, col2, col3 = st.columns(3)

        col1.metric("Indicadores", len(ratios))
        col2.metric(
            "Calculados",
            sum(r.value is not None for r in ratios),
        )
        col3.metric("Incidencias", len(issues))

        st.subheader("Resumen de ratios")
        df = ratio_table(result)

        if not df.empty:
            st.dataframe(df, use_container_width=True)

        st.subheader("Datos financieros reconocidos")
        if data:
            st.dataframe(
                pd.DataFrame(
                    list(data.items()),
                    columns=["Concepto", "Valor"],
                ),
                use_container_width=True,
            )


# ==========================================
# 2. ESTADOS FINANCIEROS
# ==========================================

elif section == "Estados financieros":
    st.header("📁 Estados financieros")

    st.write(
        "Carga un estado financiero para procesarlo "
        "con los módulos existentes del proyecto."
    )

    uploaded_file = st.file_uploader(
        "Selecciona un archivo",
        type=["xlsx", "xlsm", "xls", "csv", "pdf"],
    )

    sheet_name = None

    if uploaded_file is not None:
        st.write(f"Archivo seleccionado: **{uploaded_file.name}**")

        if Path(uploaded_file.name).suffix.lower() in {
            ".xlsx", ".xlsm", ".xls"
        }:
            sheet_name = st.text_input(
                "Nombre de la hoja de Excel (opcional)",
                value="",
                help=(
                    "Déjalo vacío para utilizar la hoja "
                    "predeterminada del lector."
                ),
            )
            sheet_name = sheet_name.strip() or None

        if st.button("Analizar estado financiero", type="primary"):
            temp_path = None

            try:
                suffix = Path(uploaded_file.name).suffix.lower()

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                with st.spinner("Analizando el archivo..."):
                    analysis = analyze_file(
                        temp_path,
                        sheet_name=sheet_name,
                    )

                st.session_state.analysis_result = analysis
                result = analysis

                if getattr(analysis, "status", "error") == "error":
                    st.error(
                        "El archivo no pudo procesarse "
                        "correctamente. Revisa las incidencias."
                    )
                else:
                    st.success("El análisis terminó.")

                st.rerun()

            except Exception as exc:
                st.error(f"No fue posible analizar el archivo: {exc}")

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    if result is not None:
        st.divider()
        st.subheader("Resultado de la última carga")

        st.write(
            "Archivo:",
            Path(getattr(result, "source_file", "")).name,
        )
        st.write(
            "Estado:",
            getattr(result, "status", "No disponible"),
        )

        metadata = getattr(result, "metadata", None) or {}

        if metadata:
            st.write("Información del procesamiento")
            st.json(metadata)

        data = getattr(result, "normalized_data", None) or {}

        if data:
            st.subheader("Datos normalizados")
            st.dataframe(
                pd.DataFrame(
                    list(data.items()),
                    columns=["Concepto", "Valor"],
                ),
                use_container_width=True,
            )


# ==========================================
# 3. RATIOS FINANCIEROS
# ==========================================

elif section == "Ratios financieros":
    st.header("📈 Ratios financieros")

    if result is None:
        st.info("Primero carga y analiza un estado financiero.")
    else:
        df = ratio_table(result)

        if df.empty:
            st.warning("El análisis no produjo indicadores.")
        else:
            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                "Descargar ratios en CSV",
                data=csv_data,
                file_name="ratios_financieros.csv",
                mime="text/csv",
            )


# ==========================================
# 4. INTERPRETACIÓN
# ==========================================

elif section == "Interpretación":
    st.header("📝 Interpretación financiera")

    if result is None:
        st.info("Primero carga y analiza un estado financiero.")
    else:
        for ratio in get_ratios(result):
            name = RATIO_NAMES.get(ratio.name, ratio.name)
            value = format_ratio(ratio.name, ratio.value)

            with st.expander(f"{name}: {value}"):
                st.write("**Fórmula:**", ratio.formula)

                interpretation = getattr(
                    ratio, "interpretation", None
                )

                if interpretation:
                    st.write("**Interpretación:**")
                    st.write(interpretation)
                else:
                    st.info("No hay interpretación disponible.")

                notes = getattr(ratio, "notes", None) or []

                if notes:
                    st.write("**Notas:**")
                    for note in notes:
                        st.write(f"- {note}")

        issues = get_issues(result)

        if issues:
            st.subheader("Incidencias de validación")

            for issue in issues:
                message = (
                    f"{issue.code}: {issue.message}"
                )
                severity = getattr(issue, "severity", "info")

                if severity == "error":
                    st.error(message)
                elif severity == "warning":
                    st.warning(message)
                else:
                    st.info(message)


# ==========================================
# PIE DE PÁGINA
# ==========================================

st.divider()

st.caption(
    "Análisis financiero de seguros | Proyecto académico"
)