# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURACIÓN Y ESTILO PROFESIONAL
# ==========================================
st.set_page_config(page_title="Executive Finance Hub", page_icon="📈", layout="wide")

# CSS para suavizar la interfaz y mejorar tarjetas
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { background-color: #ffffff; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Constantes
CATEGORIAS_GASTO = ["Alimentos", "Transporte", "Vivienda", "Servicios Publicos", "Entretenimiento", "Tecnologia", "Educacion", "Otros"]
CATEGORIAS_INGRESO = ["Salario", "Inversiones", "Freelance", "Otros Ingresos"]

# Inicialización de estado
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = pd.DataFrame(columns=["Fecha", "Tipo", "Categoria", "Descripcion", "Monto"])
if 'presupuestos' not in st.session_state:
    st.session_state.presupuestos = {cat: 500.0 for cat in CATEGORIAS_GASTO}

# ==========================================
# BARRA LATERAL: ENTRADA DE DATOS
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5551/5551144.png", width=100)
    st.header("Gestion de Activos")
    
    with st.expander("➕ Registrar Operacion"):
        tipo = st.radio("Tipo", ["Ingreso", "Gasto"])
        fecha = st.date_input("Fecha", datetime.date.today())
        lista_cats = CATEGORIAS_INGRESO if tipo == "Ingreso" else CATEGORIAS_GASTO
        cat = st.selectbox("Categoria", lista_cats)
        desc = st.text_input("Nota", "Detalle de operacion")
        monto = st.number_input("Monto ($)", min_value=0.0, step=50.0)
        
        if st.button("Confirmar Registro", use_container_width=True):
            if monto > 0:
                nueva_f = pd.DataFrame([[fecha, tipo, cat, desc, monto]], columns=st.session_state.transacciones.columns)
                st.session_state.transacciones = pd.concat([st.session_state.transacciones, nueva_f], ignore_index=True)
                st.success("Dato indexado correctamente")
            else:
                st.error("El monto debe ser mayor a 0")

    with st.expander("⚙️ Limites Presupuestarios"):
        for c in CATEGORIAS_GASTO:
            st.session_state.presupuestos[c] = st.number_input(f"{c}:", value=st.session_state.presupuestos[c], step=100.0)

# ==========================================
# CUERPO PRINCIPAL: DASHBOARD EJECUTIVO
# ==========================================
st.title("📈 Executive Finance Dashboard")
st.markdown("---")

# Filtro Temporal en la parte superior
c1, c2, c3 = st.columns([1, 1, 2])
with c1: f_inicio = st.date_input("Desde", datetime.date.today() - datetime.timedelta(days=30))
with c2: f_fin = st.date_input("Hasta", datetime.date.today())

# Procesamiento de datos
df = st.session_state.transacciones.copy()
if not df.empty:
    df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
    df = df[(df['Fecha'] >= f_inicio) & (df['Fecha'] <= f_fin)]

# --- SECCIÓN 1: KPIs GERENCIALES ---
ing = df[df['Tipo'] == "Ingreso"]['Monto'].sum()
gst = df[df['Tipo'] == "Gasto"]['Monto'].sum()
bal = ing - gst
tasa_ahorro = ((ing - gst) / ing * 100) if ing > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Ingresos Totales", f"${ing:,.0f}", delta_color="normal")
m2.metric("Gastos Totales", f"${gst:,.0f}", delta_color="inverse")
m3.metric("Flujo Neto (EBITDA)", f"${bal:,.0f}", delta=f"{tasa_ahorro:.1f}% Tasa Ahorro")
m4.metric("Eficiencia Capital", "Saludable" if bal > 0 else "Critica")

st.markdown("### Visualizacion de Resultados")
col_g1, col_g2 = st.columns(2)

with col_g1:
    # Gráfico de Dona: Distribución de Gastos
    df_gst = df[df['Tipo'] == "Gasto"]
    if not df_gst.empty:
        fig_donut = px.pie(df_gst, values='Monto', names='Categoria', hole=0.5, 
                         title="Distribucion Gerencial de Gastos",
                         color_discrete_sequence=px.colors.sequential.RdBu)
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Aun no hay gastos en este periodo")

with col_g2:
    # Gráfico de Barras: Ingresos vs Gastos
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name='Ingresos', x=['Totales'], y=[ing], marker_color='#2ecc71'))
    fig_comp.add_trace(go.Bar(name='Gastos', x=['Totales'], y=[gst], marker_color='#e74c3c'))
    fig_comp.update_layout(title="Comparativa de Flujos", barmode='group', height=400)
    st.plotly_chart(fig_comp, use_container_width=True)

# --- SECCIÓN 2: CONTROL DE PRESUPUESTOS (GAUGE STYLE) ---
st.markdown("### Control de Desviaciones (Alertas)")
cols_alert = st.columns(4)
gastos_agrupados = df_gst.groupby('Categoria')['Monto'].sum().to_dict()

for i, cat in enumerate(CATEGORIAS_GASTO):
    spent = gastos_agrupados.get(cat, 0)
    limit = st.session_state.presupuestos[cat]
    percent = (spent / limit) if limit > 0 else 0
    
    with cols_alert[i % 4]:
        st.write(f"**{cat}**")
        color = "green" if percent < 0.8 else ("orange" if percent < 1.0 else "red")
        st.progress(min(percent, 1.0))
        st.caption(f"${spent:,.0f} de ${limit:,.0f} ({percent*100:.1f}%)")

# --- SECCIÓN 3: DETALLE DE OPERACIONES ---
with st.expander("🔍 Auditoria de Movimientos"):
    st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
