import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(page_title="Dashboard Transporte", layout="wide")

COSTOS_FIJOS = 5900000

TIPOS_GASTO = [
    "Gasolina",
    "Peajes",
    "Imprevistos",
    "Aseo",
    "Consumibles",
    "Otros"
]

# --------------------------------------------------
# ESTILO (DISEÑO PRO)
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a, #1e293b);
    color: white;
}
h1,h2,h3 {color: #f97316;}
.stButton>button {
    background-color: #16a34a;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "servicios" not in st.session_state:
    st.session_state.servicios = []

if "gastos" not in st.session_state:
    st.session_state.gastos = []

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🚐 Dashboard Transporte 4x4")

# --------------------------------------------------
# TABS (APP NAVIGATION)
# --------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Dashboard",
    "📊 Gráficos",
    "📁 Cierre",
    "📚 Historial"
])

# ==================================================
# TAB 1 - DASHBOARD (FORM + ALERTAS)
# ==================================================
with tab1:

    st.subheader("Registrar Servicio")

    with st.form("form_servicio", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)

        servicio = c1.number_input("Valor servicio", min_value=0)
        fecha = c2.date_input("Fecha", value=datetime.today())
        desc = c3.text_input("Descripción", max_chars=200)

        if st.form_submit_button("Agregar Servicio"):
            if servicio > 0:
                st.session_state.servicios.append({
                    "fecha": str(fecha),
                    "valor": servicio,
                    "descripcion": desc
                })
                st.success("✅ Servicio agregado")

    st.subheader("Registrar Gasto")

    with st.form("form_gasto", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)

        gasto = c1.number_input("Valor gasto", min_value=0)
        fecha_g = c2.date_input("Fecha gasto", value=datetime.today())
        tipo = c3.selectbox("Tipo", TIPOS_GASTO)

        detalle = ""
        if tipo == "Otros":
            detalle = st.text_input("Detalle adicional", max_chars=100)

        if st.form_submit_button("Agregar Gasto"):
            if gasto > 0:
                final_desc = tipo if tipo != "Otros" else f"Otros - {detalle}"

                st.session_state.gastos.append({
                    "fecha": str(fecha_g),
                    "valor": gasto,
                    "descripcion": final_desc
                })

                st.success("✅ Gasto agregado")

    # CALCULOS
    ingresos = sum(s["valor"] for s in st.session_state.servicios)
    gastos = sum(g["valor"] for g in st.session_state.gastos)

    costo_total = COSTOS_FIJOS + gastos
    resultado = ingresos - costo_total

    # INDICADORES
    st.subheader("Indicadores")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"${ingresos:,.0f}")
    c2.metric("Costos", f"${costo_total:,.0f}")
    c3.metric("Resultado", f"${resultado:,.0f}")

    # ALERTAS INTELIGENTES
    if ingresos == 0:
        st.warning("⚠️ No hay ingresos registrados")
    elif gastos > ingresos:
        st.error("🔴 Gastos superan ingresos")
    elif resultado > 0:
        st.success("🟢 Generando ganancias")
    else:
        st.warning("🟡 Cerca del punto de equilibrio")

    if gastos > ingresos * 0.7:
        st.error("⚠️ Gastos muy altos (>70%)")

# ==================================================
# TAB 2 - GRAFICOS
# ==================================================
with tab2:

    st.subheader("📊 Análisis financiero")

    data = []
    ing_acum = 0
    gas_acum = 0

    max_len = max(len(st.session_state.servicios), len(st.session_state.gastos))

    for i in range(max_len):
        if i < len(st.session_state.servicios):
            ing_acum += st.session_state.servicios[i]["valor"]

        if i < len(st.session_state.gastos):
            gas_acum += st.session_state.gastos[i]["valor"]

        utilidad = ing_acum - (COSTOS_FIJOS + gas_acum)

        data.append({
            "Paso": i + 1,
            "Utilidad": utilidad,
            "Gastos": gas_acum
        })

    df = pd.DataFrame(data)

    if not df.empty:
        st.line_chart(df.set_index("Paso")[["Utilidad", "Gastos"]])
    else:
        st.info("Sin datos para mostrar")

# ==================================================
# TAB 3 - EXPORTAR
# ==================================================
with tab3:

    st.subheader("Cierre de mes")

    ingresos = sum(s["valor"] for s in st.session_state.servicios)
    gastos = sum(g["valor"] for g in st.session_state.gastos)
    resultado = ingresos - (COSTOS_FIJOS + gastos)

    if st.button("Finalizar mes y exportar"):

        df_serv = pd.DataFrame(st.session_state.servicios)
        df_gas = pd.DataFrame(st.session_state.gastos)

        resumen = pd.DataFrame({
            "Concepto": ["Ingresos", "Costos fijos", "Gastos", "Resultado"],
            "Valor": [ingresos, COSTOS_FIJOS, gastos, resultado]
        })

        archivo = f"reporte_{datetime.now().strftime('%Y_%m')}.xlsx"

        with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
            df_serv.to_excel(writer, sheet_name="Servicios", index=False)
            df_gas.to_excel(writer, sheet_name="Gastos", index=False)
            resumen.to_excel(writer, sheet_name="Resumen", index=False)

        with open(archivo, "rb") as f:
            st.download_button("Descargar reporte", f, file_name=archivo)

        # LIMPIAR DATOS
        st.session_state.servicios = []
        st.session_state.gastos = []

        st.success("✅ Mes cerrado correctamente")

# ==================================================
# TAB 4 - HISTORIAL
# ==================================================
with tab4:

    st.subheader("Historial")

    c1, c2 = st.columns(2)

    with c1:
        st.write("Servicios")
        st.dataframe(pd.DataFrame(st.session_state.servicios))

    with c2:
        st.write("Gastos")
        st.dataframe(pd.DataFrame(st.session_state.gastos))