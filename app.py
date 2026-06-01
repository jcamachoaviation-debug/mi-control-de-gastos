import streamlit as st
import pandas as pd
import datetime

# ==========================================
# CONSTANTES Y CONFIGURACIÓN DE LA APP
# ==========================================
CATEGORIAS_GASTO = [Alimentos, Transporte, Vivienda, Servicios Públicos, Entretenimiento, Tecnología, Educación, Otros]
CATEGORIAS_INGRESO = [Salario, Inversiones, Freelance, Otros Ingresos]

st.set_page_config(
    page_title=FinanzasPro - Control de Activos Personales,
    page_icon=📊,
    layout=wide
)

# ==========================================
# GESTIÓN DEL ESTADO DE LA APLICACIÓN (PERSISTENCIA)
# ==========================================
if 'transacciones' not in st.session_state
    # Inicializar con algunos datos de prueba para visualización inmediata
    st.session_state.transacciones = pd.DataFrame(columns=[Fecha, Tipo, Categoría, Descripción, Monto])
    
if 'presupuestos' not in st.session_state
    # Presupuestos por defecto para las alertas por tipo de gasto
    st.session_state.presupuestos = {cat 500.0 for cat in CATEGORIAS_GASTO}

# ==========================================
# INTERFAZ DE USUARIO PANEL LATERAL (INPUTS)
# ==========================================
st.sidebar.header(🕹️ Panel de Operaciones)

tab_ingreso, tab_gasto = st.sidebar.tabs([+ Ingreso, - Gasto])

with tab_ingreso
    st.subheader(Registrar Entrada de Capital)
    fecha_inc = st.date_input(Fecha, datetime.date.today(), key=f_inc)
    cat_inc = st.selectbox(Categoría, CATEGORIAS_INGRESO, key=c_inc)
    desc_inc = st.text_input(Descripción  Fuente, Pago de servicios, key=d_inc)
    monto_inc = st.number_input(Monto ($), min_value=0.0, step=10.0, key=m_inc)
    
    if st.button(Agregar Ingreso, use_container_width=True)
        nueva_fila = pd.DataFrame([[fecha_inc, Ingreso, cat_inc, desc_inc, monto_inc]], columns=st.session_state.transacciones.columns)
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nueva_fila], ignore_index=True)
        st.toast(🟢 Ingreso registrado exitosamente.)

with tab_gasto
    st.subheader(Registrar Salida de Capital)
    fecha_gst = st.date_input(Fecha, datetime.date.today(), key=f_gst)
    cat_gst = st.selectbox(Categoría, CATEGORIAS_GASTO, key=c_gst)
    desc_gst = st.text_input(Descripción  Concepto, Compra de insumos, key=d_gst)
    monto_gst = st.number_input(Monto ($), min_value=0.0, step=10.0, key=m_gst)
    
    if st.button(Agregar Gasto, use_container_width=True)
        nueva_fila = pd.DataFrame([[fecha_gst, Gasto, cat_gst, desc_gst, monto_gst]], columns=st.session_state.transacciones.columns)
        st.session_state.transacciones = pd.concat([st.session_state.transacciones, nueva_fila], ignore_index=True)
        st.toast(🔴 Gasto registrado exitosamente.)

# Configuración de Límites de Presupuesto para Alertas
st.sidebar.markdown(---)
st.sidebar.subheader(⚙️ Configurar Alertas de Presupuesto)
for cat in CATEGORIAS_GASTO
    st.session_state.presupuestos[cat] = st.sidebar.number_input(
        fLímite para {cat} ($), 
        min_value=0.0, 
        value=st.session_state.presupuestos[cat], 
        step=50.0
    )

# ==========================================
# CUERPO PRINCIPAL DE LA APLICACIÓN
# ==========================================
st.title(📊 Control de Gastos y Balance de Activos)
st.markdown(Plataforma analítica para la optimización financiera y control de fugas de capital.)

# Asegurar orden cronológico y tipo correcto de fecha
if not st.session_state.transacciones.empty
    st.session_state.transacciones['Fecha'] = pd.to_datetime(st.session_state.transacciones['Fecha']).dt.date

# ------------------------------------------
# SECCIÓN 1 CONTROL TEMPORAL (FILTRO POR FECHA)
# ------------------------------------------
st.subheader(🔍 Filtro de Balance Temporal)
col_f1, col_f2 = st.columns(2)
with col_f1
    fecha_inicio = st.date_input(Fecha Inicial, datetime.date.today() - datetime.timedelta(days=30))
with col_f2
    fecha_fin = st.date_input(Fecha Final, datetime.date.today())

# Filtrado del dataset principal
df_filtrado = st.session_state.transacciones[
    (st.session_state.transacciones['Fecha'] = fecha_inicio) & 
    (st.session_state.transacciones['Fecha'] = fecha_fin)
]

# ------------------------------------------
# SECCIÓN 2 MÉTRICAS CLAVE Y BALANCE
# ------------------------------------------
ingresos_totales = df_filtrado[df_filtrado['Tipo'] == Ingreso]['Monto'].sum()
gastos_totales = df_filtrado[df_filtrado['Tipo'] == Gasto]['Monto'].sum()
balance_neto = ingresos_totales - gastos_totales

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric(Total Ingresos, f$ {ingresos_totales,.2f}, delta=f+{ingresos_totales,.2f} if ingresos_totales  0 else None)
col_m2.metric(Total Gastos, f$ {gastos_totales,.2f}, delta=f-{gastos_totales,.2f} if gastos_totales  0 else None, delta_color=inverse)

if balance_neto = 0
    col_m3.metric(Balance Neto (Superávit), f$ {balance_neto,.2f}, delta=fRentable)
else
    col_m3.metric(Balance Neto (Déficit), f$ {balance_neto,.2f}, delta=fCrítico, delta_color=inverse)

st.markdown(---)

# ------------------------------------------
# SECCIÓN 3 MOTOR DE ALERTAS POR TIPO DE GASTO
# ------------------------------------------
st.subheader(🚨 Sistema de Alertas de Consumo y Presupuesto)

# Calcular lo gastado por categoría en el rango seleccionado
df_gastos = df_filtrado[df_filtrado['Tipo'] == Gasto]
gastos_por_cat = df_gastos.groupby('Categoría')['Monto'].sum().to_dict()

# Renderizar alertas dinámicas tipo semáforo
cols_alertas = st.columns(len(CATEGORIAS_GASTO)  2)
for idx, cat in enumerate(CATEGORIAS_GASTO)
    monto_gastado = gastos_por_cat.get(cat, 0.0)
    limite = st.session_state.presupuestos[cat]
    
    with cols_alertas[idx % len(cols_alertas)]
        if limite  0
            porcentaje = (monto_gastado  limite)  100
            
            if porcentaje = 100
                st.error(f{cat} ALERTA CRÍTICA 🔴nConsumido $ {monto_gastado,.2f}  Límite $ {limite,.2f} ({porcentaje.1f}%))
            elif porcentaje = 80
                st.warning(f{cat} Advertencia 🟡nConsumido $ {monto_gastado,.2f}  Límite $ {limite,.2f} ({porcentaje.1f}%))
            else
                st.success(f{cat} Estable 🟢nConsumido $ {monto_gastado,.2f}  Límite $ {limite,.2f} ({porcentaje.1f}%))
        else
            st.info(f{cat}nSin límite configurado. Gastado $ {monto_gastado,.2f})

st.markdown(---)

# ------------------------------------------
# SECCIÓN 4 VISUALIZACIÓN DE TRANSACCIONES Y DATOS CRUSTÁCEOS
# ------------------------------------------
col_d1, col_d2 = st.columns([3, 2])

with col_d1
    st.subheader(📋 Libro de Registro (Rango Seleccionado))
    if df_filtrado.empty
        st.info(No se registran operaciones en el rango de fechas seleccionado.)
    else
        st.dataframe(df_filtrado.sort_values(by=Fecha, ascending=False), use_container_width=True)

with col_d2
    st.subheader(📊 Distribución del Gasto)
    if not df_gastos.empty
        # Gráfico nativo rápido de barras para entender las desviaciones por categoría
        chart_data = df_gastos.groupby('Categoría')[['Monto']].sum()
        st.bar_chart(chart_data)
    else
        st.info(Sin gastos registrados para graficar.)