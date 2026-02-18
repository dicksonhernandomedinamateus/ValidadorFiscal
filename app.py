import streamlit as st
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA MOBILE-FIRST ---
st.set_page_config(
    page_title="Validador Penal",
    page_icon="⚖️",
    layout="centered"
)

def app():
    # --- TÍTULO Y CRÉDITOS ---
    st.title("⚖️ VALIDADOR PENAL")
    st.markdown("**Omisión de Activos (434A) y Evasión (434B)**")
    
    with st.expander("ℹ️ Créditos"):
        st.markdown(
            """
            * **Programador:** Dickson Hernando Medina Mateus
            * **Jefe:**        Jorge Iván Rodríguez
           
            """
        )

  # --- BASE DE DATOS SMLMV ---
    smlmv_db = {
        2017: 737717, 2018: 781242, 2019: 828116, 2020: 877803,
        2021: 908526, 2022: 1000000, 2023: 1160000, 2024: 1300000,
        2025: 1423500, 2026: 1565850
    }

    st.markdown("---")
    st.subheader("1. Filtros de Viabilidad")

    # 1. FECHA (DETERMINA LA LEY APLICABLE)
    col_fecha, col_anio = st.columns([2, 1])
    with col_fecha:
        fecha_hechos = st.date_input(
            "Fecha de presentación / hechos:",
            min_value=date(2017, 1, 1),
            max_value=date(2026, 12, 31),
            value=date(2024, 1, 1)
        )
    
    anio = fecha_hechos.year
    smlmv_anio = smlmv_db.get(anio, 1300000)
    
    with col_anio:
        st.info(f"**Año:** {anio}")

    # --- FILTRO 1: SUJETO ACTIVO (Solo si es < 2023) ---
    if anio < 2023:
        es_contribuyente = st.radio(
            "¿El sujeto tenía la calidad de 'Contribuyente'?",
            options=["SÍ", "NO"],
            horizontal=True,
            key="filtro_contribuyente"
        )
        if es_contribuyente == "NO":
            st.warning("⛔ **STOP:** No hay delito, Para esta fecha la ley exigía ser Contribuyente.")
            return # DETIENE LA EJECUCIÓN AQUÍ

    # --- FILTRO 2: PROCEDIBILIDAD (LIQUIDACIÓN OFICIAL) ---
    tiene_liquidacion = st.radio(
        "¿Existe ya Liquidación Oficial de Autoridad Competente?",
        options=["SÍ", "NO"],
        horizontal=True,
        key="filtro_liquidacion"
    )
    
    if tiene_liquidacion == "NO":
        st.warning("⛔ **STOP:** No hay delito")
        st.info("Sin Liquidación Oficial, el caso está en etapa administrativa.")
        return # DETIENE LA EJECUCIÓN AQUÍ

    # ---------------------------------------------------------
    # SI PASA LOS FILTROS, MUESTRA EL RESTO DEL FORMULARIO
    # ---------------------------------------------------------

    st.markdown("---")
    st.subheader("2. Análisis de Conducta")
    
    # 3. SELECCIÓN DE TIPO PENAL Y VERBOS
    tipo_delito = st.radio(
        "Seleccione el Tipo Penal:",
        options=["Art. 434A (Activos/Pasivos)", "Art. 434B (Defraudación/Evasión)"],
        horizontal=True
    )

    verbo_seleccionado = ""
    
    # LÓGICA DE VERBOS 434A
    if "434A" in tipo_delito:
        if 2017 <= anio <= 2019:
            lista_verbos = ["Omitir activos", "Presentar información inexacta en activos", "Declarar pasivos inexistentes"]
        else:
            lista_verbos = ["Omitir activos", "Declarar menor valor de los activos", "Declarar pasivos inexistentes"]
        verbo_seleccionado = st.selectbox("Conducta específica:", lista_verbos)

    # LÓGICA DE VERBOS 434B
    elif "434B" in tipo_delito:
        if anio < 2020:
            st.error("⛔ **ATIPICIDAD:** El Art. 434B no era aplicable antes de 2020.")
            return
        lista_verbos = ["Omitir ingresos", "Incluir costos/gastos inexistentes", "Créditos fiscales improcedentes"]
        verbo_seleccionado = st.selectbox("Conducta específica:", lista_verbos)

    # 4. VALOR
    monto_irregularidad = st.number_input(
        "💰 Valor de la irregularidad (Pesos COP):",
        min_value=0.0, format="%.0f"
    )

    # --- BOTÓN DE ANÁLISIS ---
    if st.button("🔍 CALCULAR UMBRAL", type="primary", use_container_width=True):
        st.markdown("---")
        
        # CÁLCULO DE UMBRALES
        umbral_smlmv = 0
        norma = ""

        if "434A" in tipo_delito:
            if 2017 <= anio <= 2019:
                umbral_smlmv = 7250
                norma = "Ley 1819 de 2016"
            elif 2020 <= anio <= 2022:
                umbral_smlmv = 5000
                norma = "Ley 2010 de 2019"
            elif anio >= 2023:
                umbral_smlmv = 1000
                norma = "Ley 2277 de 2022"

        elif "434B" in tipo_delito:
            if 2020 <= anio <= 2022:
                umbral_smlmv = 250
                norma = "Ley 2010 de 2019"
            elif anio >= 2023:
                umbral_smlmv = 100
                norma = "Ley 2277 de 2022"

        # RESULTADOS
        valor_umbral_pesos = umbral_smlmv * smlmv_anio
        
        st.subheader("📊 Resultado Final")
        col1, col2 = st.columns(2)
        col1.metric("Monto del Caso", f"${monto_irregularidad:,.0f}")
        col2.metric("Umbral Legal", f"${valor_umbral_pesos:,.0f}", f"{umbral_smlmv} SMLMV")
        
        st.caption(f"Norma: {norma} | SMLMV Año {anio}: ${smlmv_anio:,.0f}")

        if monto_irregularidad >= valor_umbral_pesos:
            st.error("🚨 **HAY DELITO **")
            st.write(f"El monto supera el tope penal vigente en {anio}.")
        else:
            st.success("🟢 **NO ES DELITO **")
            diff = valor_umbral_pesos - monto_irregularidad
            st.write(f"Faltan ${diff:,.0f} para alcanzar el umbral penal.")

if __name__ == "__main__":
    app()



