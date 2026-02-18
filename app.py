import streamlit as st
from datetime import date

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Validador Penal Fiscal", page_icon="⚖️")

def app():
    # --- ENCABEZADO Y CRÉDITOS ---
    st.markdown("---")
    st.title("⚖️ VALIDADOR DE DELITOS FISCALES")
    st.markdown("### OMISIÓN DE ACTIVOS (434A) Y EVASIÓN (434B)")
    
    st.info(
        """
        **DESARROLLADO POR:**
        * **Autor y Concepto Jurídico:** Dickson Hernando Medina Mateus
        * **Co-piloto Tecnológico:** Gemini AI
        * **Alcance:** Verificación de Umbrales (SMLMV) y Requisito de Procedibilidad.
        """
    )
    st.markdown("---")

    # --- BASE DE DATOS: HISTÓRICO SMLMV ---
    smlmv_db = {
        2017: 737717,
        2018: 781242,
        2019: 828116,
        2020: 877803,
        2021: 908526,
        2022: 1000000,
        2023: 1160000,
        2024: 1300000,
        2025: 1423500, 
        2026: 1565850 
    }

    # --- ENTRADAS (SIDEBAR) ---
    st.sidebar.header("1. Datos del Caso")
    
    # 1. FECHA
    fecha_hechos = st.sidebar.date_input(
        "Fecha de presentación de la declaración o hechos",
        min_value=date(2017, 1, 1),
        max_value=date(2026, 12, 31),
        value=date(2024, 1, 1)
    )
    anio = fecha_hechos.year
    smlmv_anio = smlmv_db.get(anio, 1300000)
    
    st.sidebar.markdown(f"**Año Fiscal:** {anio} | **SMLMV:** ${smlmv_anio:,.0f}")

    # 2. TIPO PENAL
    tipo_delito = st.sidebar.radio(
        "¿Qué conducta se investiga?",
        options=["Art. 434A (Activos/Pasivos)", "Art. 434B (Defraudación/Evasión)"]
    )

    # 3. VALOR
    monto_irregularidad = st.sidebar.number_input(
        "Valor de la irregularidad (Pesos COP)",
        min_value=0.0,
        format="%.2f"
    )

    # 4. ESTADO PROCESAL
    st.sidebar.header("2. Estado Procesal")
    tiene_liquidacion = st.sidebar.radio(
        "¿Existe Liquidación Oficial o Resolución Sanción?",
        options=["NO (Etapa Persuasiva/Fiscalización)", "SÍ (Acto Administrativo Oficial)"]
    )

    # --- BOTÓN DE ANÁLISIS ---
    if st.button("ANALIZAR CASO AHORA", type="primary"):
        
        # FILTRO DE PROCEDIBILIDAD
        if "NO" in tiene_liquidacion:
            st.warning("⚠️ **ANÁLISIS DE PROCEDIBILIDAD: DETENIDO**")
            st.markdown(f"""
            Aunque exista una irregularidad de **${monto_irregularidad:,.0f}**, **NO se configura el delito procesalmente**.
            
            **Razón Jurídica:** El tipo penal exige que exista una **Liquidación Oficial** de la autoridad tributaria.
            """)
            st.success("✅ **CONCLUSIÓN:** El contribuyente está a tiempo de corregir en etapa administrativa sin riesgo penal inmediato.")
            return

        # CÁLCULO DE UMBRALES
        umbral_smlmv = 0
        norma = ""
        
        # LÓGICA 434A
        if "434A" in tipo_delito:
            if 2017 <= anio <= 2019:
                norma = "Ley 1819 de 2016"
                umbral_smlmv = 7250
            elif 2020 <= anio <= 2022:
                norma = "Ley 2010 de 2019"
                umbral_smlmv = 5000
            elif anio >= 2023:
                norma = "Ley 2277 de 2022"
                umbral_smlmv = 1000
                st.info("ℹ️ Nota: Desde 2023, NO se requiere sujeto activo calificado.")

        # LÓGICA 434B
        elif "434B" in tipo_delito:
            if anio < 2020:
                st.error("⛔ **ATIPICIDAD:** El Art. 434B no era aplicable antes de 2020.")
                return
            elif 2020 <= anio <= 2022:
                norma = "Ley 2010 de 2019"
                umbral_smlmv = 250
            elif anio >= 2023:
                norma = "Ley 2277 de 2022"
                umbral_smlmv = 100

        # RESULTADOS MATEMÁTICOS
        valor_umbral_pesos = umbral_smlmv * smlmv_anio
        
        st.subheader(f"📊 Resultados del Análisis ({anio})")
        col1, col2 = st.columns(2)
        col1.metric("Tu Caso (Monto)", f"${monto_irregularidad:,.0f}")
        col2.metric("Umbral Penal (Tope)", f"${valor_umbral_pesos:,.0f}", f"{umbral_smlmv} SMLMV")

        st.markdown(f"**Norma Aplicada:** {norma}")

        if monto_irregularidad >= valor_umbral_pesos:
            st.error("🚨 **RESULTADO: CONDUCTA TÍPICA (HAY DELITO)**")
            st.markdown(f"El monto supera los **{umbral_smlmv} SMLMV** exigidos por la ley vigente en {anio}.")
            st.markdown("⚠️ **Acción:** Se recomienda pago inmediato o defensa penal especializada.")
        else:
            st.success("🟢 **RESULTADO: CONDUCTA ATÍPICA (NO ES DELITO)**")
            diferencia = valor_umbral_pesos - monto_irregularidad
            st.markdown(f"El monto NO alcanza la cuantía penal. Faltarían **${diferencia:,.0f}** para ser delito.")

if __name__ == "__main__":
    app()