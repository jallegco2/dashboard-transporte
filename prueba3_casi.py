import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(page_title="Dashboard Transporte", layout="wide")

TIPOS_GASTO = [
    "Gasolina", "Peajes", "Imprevistos",
    "Aseo", "Consumibles", "Otros"
]

# --------------------------------------------------
# FUNCIONES (OPTIMIZACIÓN)
# --------------------------------------------------
def calcular_ingresos():
    return sum(s["valor"] for s in st.session_state.servicios)

def calcular_gastos():
    return sum(g["valor"] for g in st.session_state.gastos)

def calcular_fijos():
    pagados = sum(g["valor"] for g in st.session_state.gastos_fijos if g["pagado"])
    pendientes = sum(g["valor"] for g in st.session_state.gastos_fijos if not g["pagado"])
    return pagados, pendientes

def validar_lista(lista):
    return lista if lista else []

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "servicios" not in st.session_state:
    st.session_state.servicios = []

if "gastos" not in st.session_state:
    st.session_state.gastos = []

if "gastos_fijos" not in st.session_state:
    st.session_state.gastos_fijos = [
        {"descripcion": "Salario Conductor", "valor": 2500000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Crédito vehículo", "valor": 1830000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Seguros Todo Riesgo", "valor": 350000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Administración", "valor": 170000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Seguridad Social", "valor": 500000, "pagado": False, "fecha_pago": None},
        {"descripcion": "SOAT", "valor": 35000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Revisión Bimensual", "valor": 20000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Tecnicomecanica", "valor": 35000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Poliza Contractual", "valor": 125000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Tarjeta Operación", "valor": 10000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Ahorro imprevistos", "valor": 20000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Abono Credito", "valor": 20000, "pagado": False, "fecha_pago": None},
    ]

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🚐 Dashboard Transporte 4x4")

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "📊 Gráficos",
    "📁 Cierre",
    "📚 Historial",
    "💼 Gastos Fijos"
])

# ==================================================
# TAB 1 - DASHBOARD
# ==================================================
with tab1:

    st.subheader("Registrar Servicio")

    with st.form("form_servicio", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)

        servicio = c1.number_input("Valor servicio", min_value=0)
        fecha = c2.date_input("Fecha", value=datetime.today())
        desc = c3.text_input("Descripción")

        if st.form_submit_button("Agregar"):
            if servicio > 0:
                st.session_state.servicios.append({
                    "fecha": str(fecha),
                    "valor": servicio,
                    "descripcion": desc
                })
                st.success("✅ Servicio agregado")

    # -----------------------------
    st.subheader("Registrar Gasto")

    with st.form("form_gasto", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)

        gasto = c1.number_input("Valor gasto", min_value=0)
        fecha_g = c2.date_input("Fecha gasto", value=datetime.today())
        tipo = c3.selectbox("Tipo", TIPOS_GASTO)

        detalle = st.text_input("Detalle") if tipo == "Otros" else ""

        if st.form_submit_button("Agregar"):
            if gasto > 0:
                desc = tipo if tipo != "Otros" else f"Otros - {detalle}"
                st.session_state.gastos.append({
                    "fecha": str(fecha_g),
                    "valor": gasto,
                    "descripcion": desc
                })
                st.success("✅ Gasto agregado")

    # -----------------------------
    ingresos = calcular_ingresos()
    gastos = calcular_gastos()
    fijos_pagados, fijos_pendientes = calcular_fijos()

    costo_total = gastos + fijos_pagados
    resultado = ingresos - costo_total

    st.subheader("Indicadores")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos", f"${ingresos:,.0f}")
    c2.metric("Costos Variables", f"${costo_total:,.0f}")
    c3.metric("Utilidad", f"${resultado:,.0f}")

    st.subheader("Estado de gastos fijos")

    c1, c2 = st.columns(2)
    c1.metric("Pagados", f"${fijos_pagados:,.0f}")
    c2.metric("Pendientes", f"${fijos_pendientes:,.0f}")

# ==================================================
# TAB 5 - ✅ CONTROL GASTOS FIJOS (NUEVO)
# ==================================================
with tab5:

    st.subheader("💼 Control de Gastos Fijos")

    total_fijos_pagados, total_fijos_pendientes = calcular_fijos()

    for i, g in enumerate(st.session_state.gastos_fijos):

        col1, col2, col3 = st.columns([1, 4, 2])

        with col1:
            pagado = st.checkbox("", value=g["pagado"], key=f"chk_{i}")

        with col2:
            estado = "🟢 PAGADO" if pagado else "🔴 PENDIENTE"
            st.write(f"{g['descripcion']} - ${g['valor']:,.0f} | {estado}")

        with col3:
            fecha_pago = st.date_input(
                "Fecha",
                value=g["fecha_pago"] or datetime.today(),
                key=f"fecha_{i}"
            ) if pagado else None

        st.session_state.gastos_fijos[i]["pagado"] = pagado
        st.session_state.gastos_fijos[i]["fecha_pago"] = fecha_pago

    st.divider()

    c1, c2 = st.columns(2)
    c1.metric("Total Pagados", f"${total_fijos_pagados:,.0f}")
    c2.metric("Total Pendientes", f"${total_fijos_pendientes:,.0f}")

# ==================================================
# TAB 2 - GRAFICOS
# ==================================================
with tab2:

    st.subheader("📊 Análisis financiero")

    data = []
    ing_acum = 0
    gas_acum = 0

    servicios = validar_lista(st.session_state.servicios)
    gastos_var = validar_lista(st.session_state.gastos)

    max_len = max(len(servicios), len(gastos_var))

    for i in range(max_len):

        if i < len(servicios):
            ing_acum += servicios[i]["valor"]

        if i < len(gastos_var):
            gas_acum += gastos_var[i]["valor"]

        utilidad = ing_acum - gas_acum
        data.append({"Paso": i + 1, "Utilidad": utilidad, "Gastos": gas_acum})

    df = pd.DataFrame(data)

    if not df.empty:
        st.line_chart(df.set_index("Paso"))
    else:
        st.info("Sin datos")

# ==================================================
# TAB 3 - EXPORTAR
# ==================================================
with tab3:

    st.subheader("CierreMesLABORAL")

    ingresos = calcular_ingresos()
    gastos = calcular_gastos()
    fijos_pagados, fijos_pendientes = calcular_fijos()

    costo_total = gastos + fijos_pagados
    resultado = ingresos - costo_total

    if st.button("Exportar"):

        df_serv = pd.DataFrame(validar_lista(st.session_state.servicios))
        df_gas = pd.DataFrame(validar_lista(st.session_state.gastos))
        df_fijos = pd.DataFrame(validar_lista(st.session_state.gastos_fijos))

        resumen = pd.DataFrame({
            "Concepto": ["Ingresos", "Fijos", "Gastos", "Resultado"],
            "Valor": [ingresos, fijos_pagados, gastos, resultado]
        })

        archivo = f"reporte_{datetime.now().strftime('%Y_%m')}.xlsx"

        with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
            df_serv.to_excel(writer, "Servicios", index=False)
            df_gas.to_excel(writer, "Gastos", index=False)
            df_fijos.to_excel(writer, "Fijos", index=False)
            resumen.to_excel(writer, "Resumen", index=False)

        with open(archivo, "rb") as f:
            st.download_button("Descargar", f, archivo)

        st.success("✅ Exportado correctamente")




# ==================================================
# TAB 5 - 💼 GASTOS FIJOS (FORM + DATAFRAME)
# ==================================================
with tab5:

    st.subheader("💼 Gestión de Gastos Fijos")

    # --------------------------------------------------
    # INICIALIZAR DATAFRAME EN SESSION
    # --------------------------------------------------
    if "df_fijos" not in st.session_state:
        st.session_state.df_fijos = pd.DataFrame([
        {"descripcion": "Salario Conductor", "valor": 2500000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Crédito vehículo", "valor": 1830000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Seguros Todo Riesgo", "valor": 350000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Administración", "valor": 170000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Seguridad Social", "valor": 500000, "pagado": False, "fecha_pago": None},
        {"descripcion": "SOAT", "valor": 35000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Revisión Bimensual", "valor": 20000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Tecnicomecanica", "valor": 35000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Poliza Contractual", "valor": 125000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Tarjeta Operación", "valor": 10000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Ahorro imprevistos", "valor": 20000, "pagado": False, "fecha_pago": None},
        {"descripcion": "Abono Credito", "valor": 20000, "pagado": False, "fecha_pago": None},
        ])

    df = st.session_state.df_fijos

    # --------------------------------------------------
    # FORMULARIO: AGREGAR NUEVO GASTO FIJO
    # --------------------------------------------------
    st.markdown("### ➕ Agregar gasto fijo")

    with st.form("form_fijo", clear_on_submit=True):
        c1, c2 = st.columns(2)

        desc = c1.text_input("Descripción")
        valor = c2.number_input("Valor", min_value=0)

        if st.form_submit_button("Agregar"):
            if desc and valor > 0:
                nuevo = pd.DataFrame([{
                    "descripcion": desc,
                    "valor": valor,
                    "pagado": False,
                    "fecha_pago": None
                }])
                st.session_state.df_fijos = pd.concat([df, nuevo], ignore_index=True)
                st.success("✅ Gasto fijo agregado")

    st.divider()

    # --------------------------------------------------
    # TABLA EDITABLE (queda comentada ya que duplicaba el listado de gastos fijos)
    # --------------------------------------------------
#    st.markdown("### 📋 Control de pagos")

#   df_edit = st.data_editor(
#      st.session_state.df_fijos,
#       use_container_width=True,
#       num_rows="dynamic"
#    )

#   # Guardar cambios automáticamente
#   st.session_state.df_fijos = df_edit

    # --------------------------------------------------
    # CÁLCULOS
    # --------------------------------------------------
    df = st.session_state.df_fijos

    if not df.empty:

        total_pagados = df[df["pagado"] == True]["valor"].sum()
        total_pendientes = df[df["pagado"] == False]["valor"].sum()

        c1, c2 = st.columns(2)
        c1.metric("Total Pagados", f"${total_pagados:,.0f}")
        c2.metric("Total Pendientes", f"${total_pendientes:,.0f}")

    else:
        st.info("No hay gastos fijos registrados")

    st.divider()


# ==================================================
# TAB 4 - HISTORIAL
# ==================================================
with tab4:

    st.subheader("Historial")

    c1, c2, c3 = st.columns(3)

    c1.dataframe(pd.DataFrame(validar_lista(st.session_state.servicios)))
    c2.dataframe(pd.DataFrame(validar_lista(st.session_state.gastos)))
    c3.dataframe(pd.DataFrame(validar_lista(st.session_state.gastos_fijos)))

# ==========================
# ✅ CIERRE DE MES
# ==========================
st.subheader("📁 Cierre de mes LABORAL")

if st.button("Finalizar mes & exportar"):

    df_servicios = pd.DataFrame(st.session_state.servicios)
    df_gastos = pd.DataFrame(st.session_state.gastos)

    resumen = pd.DataFrame({
        "Concepto": ["Ingresos", "Costos", "Utilidad", "Costos_Fijos_Pagados", "Costos_Fijos_Pendientes"],
        "Valor": [ingresos, costo_total, resultado, fijos_pagados, fijos_pendientes]
    })

    archivo = f"reporte_{datetime.now().strftime('%Y_%m')}.xlsx"

    with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
        df_servicios.to_excel(writer, sheet_name="Servicios", index=False)
        df_gastos.to_excel(writer, sheet_name="Gastos", index=False)
        resumen.to_excel(writer, sheet_name="Resumen", index=False)

    with open(archivo, "rb") as f:
        st.download_button("Descargar reporte", f, file_name=archivo)

    # limpiar datos
    st.session_state.servicios = []
    st.session_state.gastos = []
#    st.session_state.df_fijos = []
    

    st.success("✅ Mes cerrado correctamente")


