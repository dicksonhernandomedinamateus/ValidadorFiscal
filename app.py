import streamlit as st
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA (Para que se vea bien en móviles) ---
st.set_page_config(
    page_title="Validador Delitos Fiscales",
    page_icon="⚖️",
    layout="centered" # Centrado se ve mejor en celular que "wide"
)

def app():
    # --- TÍTULO COMPACTO ---
    st.title("⚖️ VALIDADOR DELITOS FISCALES")
    st.markdown("**Omisión de Activos (434A) y Evasión (434B)**")
    
    # Créditos en un desplegable pequeño para no estorbar
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

    # --- ENTRADAS EN EL CUERPO PRINCIPAL (NO SIDEBAR) ---
    # Usamos un contenedor con borde para que parezca un formulario
    st.markdown("---")
    st.subheader("1. Ingresa los Datos")
    
    # FECHA
    col_fecha, col_anio = st.columns([2, 1])
    with col_fecha:
        fecha_hechos = st.date_input(
            "Fecha de hechos",
            min_value=date(2017, 1, 1),
            max_value=date(2026, 12, 31),
            value=date(2024, 1, 1)
        )
    
    anio = fecha_hechos.year
    smlmv_anio = smlmv_db.get(anio, 1300000)
    
    with col_anio:
        st.info(f"**Año:** {anio}")

    # CONDUCTA (Radio button horizontal es más fácil de tocar en celular)
    tipo_delito = st.radio(
        "Conducta investigada:",
        options=["Art. 434A (Activos)", "Art. 434B (Evasión)"],
        horizontal=True
    )

    # VALOR Y ESTADO
    monto_irregularidad = st.number_input(
        "💰 Valor de la irregularidad (COP):",
        min_value=0.0,
        format="%.0f",
        help="Escribe el valor sin puntos ni comas"
    )

    tiene_liquidacion = st.checkbox(
        "✅ ¿Ya existe Liquidación Oficial DIAN?",
        help="Marca esta casilla SOLO si ya hay un acto administrativo oficial."
    )

    # --- BOTÓN GRANDE Y LLAMATIVO ---
    if st.button("🔍 ANALIZAR AHORA", type="primary", use_container_width=True):
        
        st.markdown("---")
        st.subheader("📊 Resultados")

        # 1. FILTRO PROCEDIBILIDAD
        if not tiene_liquidacion:
            st.warning("⚠️ **PROCESO DETENIDO**")
            st.write("Aunque el monto sea alto, **NO hay delito aún**.")
            st.info("Falta la Liquidación Oficial. Estás en etapa administrativa.")
            return

        # 2. CÁLCULO DE UMBRALES
        umbral_smlmv = 0
        norma = ""

        # Lógica 434A
        if "434A" in tipo_delito:
            if 2017 <= anio <= 2019:
                umbral_smlmv = 7250
                norma = "Ley 1819/16"
            elif 2020 <= anio <= 2022:
                umbral_smlmv = 5000
                norma = "Ley 2010/19"
            elif anio >= 2023:
                umbral_smlmv = 1000
                norma = "Ley 2277/22"

        # Lógica 434B
        elif "434B" in tipo_delito:
            if anio < 2020:
                st.error("El Art. 434B no aplicaba antes de 2020.")
                return
            elif 2020 <= anio <= 2022:
                umbral_smlmv = 250
                norma = "Ley 2010/19"
            elif anio >= 2023:
                umbral_smlmv = 100
                norma = "Ley 2277/22"

        # Cálculos Finales
        valor_umbral_pesos = umbral_smlmv * smlmv_anio
        
        # TARJETAS DE RESULTADO (Metrics se ven genial en celular)
        col1, col2 = st.columns(2)
        col1.metric("Tu Caso", f"${monto_irregularidad:,.0f}")
        col2.metric("Tope Penal", f"${valor_umbral_pesos:,.0f}", f"{umbral_smlmv} SMLMV")
        
        st.caption(f"Norma aplicada: {norma} (SMLMV ${smlmv_anio:,.0f})")

        # VEREDICTO FINAL
        if monto_irregularidad >= valor_umbral_pesos:
            st.error("🚨 **HAY DELITO (CONDUCTA TÍPICA)**")
            st.write("El monto supera el tope legal. Se recomienda abogado penalista.")
        else:
            st.success("🟢 **NO ES DELITO (ATÍPICO)**")
            diff = valor_umbral_pesos - monto_irregularidad
            st.write(f"Faltan **${diff:,.0f}** para que sea penal.")

if __name__ == "__main__":
    app()

