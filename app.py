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
    st.title("⚖️ VALIDADOR DELITOS FISCALES")
    st.markdown("**Omisión de Activos (434A) y Evasión (434B)**")
    
    with st.expander("ℹ️ Créditos y Autoría"):
        st.markdown(
            """
            * **Programador:** Dickson Hernando Medina Mateus
            * **Jefe:** Jorge Iván Rodríguez
           
            """
        )

    # --- BASE DE DATOS SMLMV ---
    smlmv_db = {
        2017: 737717, 2018: 781242, 2019: 828116, 2020: 877803,
        2021: 908526, 2022: 1000000, 2023: 1160000, 2024: 1300000,
        2025: 1423500, 2026: 1565850
    }

    st.markdown("---")
    st.subheader("1. Vigencia y Sujeto")

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

    # 2. VALIDACIÓN DE SUJETO ACTIVO (CONTRIBUYENTE)
    # Según tu estudio: Antes de 2023 requiere ser contribuyente. Desde 2023 NO.
    es_contribuyente = True # Por defecto
    
    if anio < 2023:
        es_contribuyente_check = st.radio(
            f"En el año {anio}, ¿el sujeto tenía la calidad de 'Contribuyente'?",
            options=["SÍ", "NO"],
            horizontal=True,
            help="Para esta vigencia, el tipo penal exige sujeto activo calificado."
        )
        if es_contribuyente_check == "NO":
            st.warning("⛔ **NO HAY DELITO:** Para la fecha seleccionada, la ley exigía que el sujeto fuera Contribuyente.")
            return # Detener ejecución
    else:
        st.info("ℹ️ **Nota:** Para el año 2023 en adelante, la ley NO exige ser contribuyente (Sujeto no calificado).")

    # 3. SELECCIÓN DE TIPO PENAL Y VERBOS RECTORES (DINÁMICOS)
    st.markdown("---")
    st.subheader("2. Conducta Investigada")
    
    tipo_delito = st.radio(
        "Seleccione el Tipo Penal:",
        options=["Art. 434A (Activos/Pasivos)", "Art. 434B (Defraudación/Evasión)"],
        horizontal=True
    )

    verbo_seleccionado = ""
    
    # LÓGICA DE VERBOS PARA 434A
    if "434A" in tipo_delito:
        if 2017 <= anio <= 2019:
            # Ley 1819: Verbo "Información Inexacta"
            lista_verbos = [
                "Omitir activos",
                "Presentar información inexacta en activos",
                "Declarar pasivos inexistentes"
            ]
        else:
            # Ley 2010 y 2277: Verbo "Menor Valor"
            lista_verbos = [
                "Omitir activos",
                "Declarar menor valor de los activos",
                "Declarar pasivos inexistentes"
            ]
        
        verbo_seleccionado = st.selectbox("¿Cuál fue la conducta específica?", lista_verbos)

    # LÓGICA DE VERBOS PARA 434B
    elif "434B" in tipo_delito:
        if anio < 2020:
            st.error("⛔ **ATIPICIDAD:** El Art. 434B no era aplicable antes de 2020.")
            return
        
        # Lista general para 434B
        lista_verbos = [
            "Omitir ingresos",
            "Incluir costos o gastos inexistentes",
            "Reclamar créditos fiscales improcedentes"
        ]
        verbo_seleccionado = st.selectbox("¿Cuál fue la conducta específica?", lista_verbos)
        
        if anio >= 2023:
            st.caption("Nota: Desde 2023 se requiere probar el 'propósito de defraudación'.")

    # 4. VALOR Y PROCEDIBILIDAD
    monto_irregularidad = st.number_input(
        "💰 Valor de la irregularidad (Pesos COP):",
        min_value=0.0, format="%.0f"
    )

    tiene_liquidacion = st.checkbox(
        "✅ ¿Existe Liquidación Oficial / Resolución Sanción?",
        help="Requisito indispensable de procedibilidad."
    )

    # --- BOTÓN DE ANÁLISIS ---
    if st.button("🔍 ANALIZAR AHORA", type="primary", use_container_width=True):
        st.markdown("---")
        
        # 1. FILTRO PROCEDIBILIDAD
        if not tiene_liquidacion:
            st.warning("⚠️ **PROCESO DETENIDO**")
            st.write("Falta el requisito de procedibilidad (Liquidación Oficial).")
            st.success("El contribuyente está en etapa administrativa. No hay delito procesal.")
            return

        # 2. CÁLCULO DE UMBRALES SEGÚN TU ESTUDIO
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

        # CÁLCULOS
        valor_umbral_pesos = umbral_smlmv * smlmv_anio
        
        # RESULTADOS
        st.subheader("📊 Resultados")
        col1, col2 = st.columns(2)
        col1.metric("Monto Caso", f"${monto_irregularidad:,.0f}")
        col2.metric("Umbral Legal", f"${valor_umbral_pesos:,.0f}", f"{umbral_smlmv} SMLMV")
        
        st.markdown(f"**Norma:** {norma} | **Verbo:** {verbo_seleccionado}")

        if monto_irregularidad >= valor_umbral_pesos:
            st.error("🚨 **HAY DELITO (CONDUCTA TÍPICA)**")
            st.write(f"Se supera el umbral de {umbral_smlmv} SMLMV y se cumple la condición de sujeto.")
        else:
            st.success("🟢 **NO ES DELITO (ATÍPICO)**")
            diff = valor_umbral_pesos - monto_irregularidad
            st.write(f"La cuantía no alcanza para ser delito penal. Faltan ${diff:,.0f}.")

if __name__ == "__main__":
    app()


