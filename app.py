# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import re

# ==========================================
# CONFIGURACIÓN PROFESIONAL ADAPTATIVA
# ==========================================
st.set_page_config(page_title="Executive Finance Hub", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: bold; }
    div[data-testid="stExpander"] { border-radius: 10px; margin-bottom: 15px; }
    .ai-box { background-color: #1e293b; color: #f8fafc; padding: 20px; border-radius: 12px; border-left: 5px solid #ef4444; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Constantes
CATEGORIAS_GASTO = ["Alimentos", "Transporte", "Vivienda", "Servicios Publicos", "Entretenimiento", "Tecnologia", "Educacion", "Otros"]
CATEGORIAS_INGRESO = ["Salario", "Inversiones", "Freelance", "Otros Ingresos"]

if 'transacciones' not in st.session_state:
    st.session_state.transacciones = pd.DataFrame(columns=["Fecha", "Tipo", "Categoria", "Descripcion", "Monto"])
if 'presupuestos' not in st.session_state:
    st.session_state.presupuestos = {cat: 500.0 for cat in CATEGORIAS_GASTO}

# ==========================================
# MOTOR NLP AVANZADO (PROCESAMIENTO DE VOZ)
# ==========================================
def procesar_comando_voz_avanzado(texto):
    texto = texto.lower()
    hoy = datetime.date.today()
    
    fecha_detectada = hoy
    if "ayer" in texto:
        fecha_detectada = hoy - datetime.timedelta(days=1)
    elif "antier" in texto or "antes de ayer" in texto:
        fecha_detectada = hoy - datetime.timedelta(days=2)
    elif "hace" in texto:
        dias_match = re.search(r'hace\s+(\d+)\s+días', texto)
        if dias_match:
            fecha_detectada = hoy - datetime.timedelta(days=int(dias_match.group(1)))
            
    dias_semana = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2, 
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }
    for dia, num_dia in dias_semana.items():
        if f"el {dia}" in texto or f"del {dia}" in texto:
            dias_atras = hoy.weekday() - num_dia
            if dias_atras <= 0:
                dias_atras += 7
            fecha_detectada = hoy - datetime.timedelta(days=dias_atras)
            break

    tipo_detectado = "Gasto"
    palabras_ingreso = ["ingreso", "recibi", "pago", "salario", "gane", "sueldo", "me depositaron", "comision", "ventas"]
    if any(palabra in texto for palabra in palabras_ingreso):
        tipo_detectado = "Ingreso"

    texto_limpio = re.sub(r'(\d+)\.(\d{3})', r'\1\2', texto)
    numeros = re.findall(r'\d+', texto_limpio)
    monto_detectado = float(numeros[0]) if numeros else 0.0

    categoria_detectada = "Otros"
    diccionario_semantico = {
        "Alimentos": ["comida", "almuerzo", "restaurante", "mercado", "supermercado", "cena", "cafe", "hamburguesa", "desayuno"],
        "Transporte": ["gasolina", "uber", "taxi", "bus", "peaje", "carro", "moto", "parqueadero", "combustible"],
        "Vivienda": ["arriendo", "alquiler", "hipoteca", "reparacion", "muebles", "reparación"],
        "Servicios Publicos": ["luz", "agua", "gas", "internet", "telefono", "celular", "servicios", "netflix", "spotify"],
        "Entretenimiento": ["cine", "fiesta", "bar", "cerveza", "concierto", "viaje", "paseo", "rumba", "discoteca"],
        "Tecnologia": ["computador", "celular", "software", "pantalla", "audifonos", "gadget", "laptop"],
        "Educacion": ["curso", "universidad", "colegio", "libro", "matricula", "seminario", "pensum"]
    }
    
    lista_analisis = CATEGORIAS_INGRESO if tipo_detectado == "Ingreso" else CATEGORIAS_GASTO
    for cat_clave, palabras_asociadas in diccionario_semantico.items():
        if any(palabra in texto for palabra in palabras_asociadas):
            if cat_clave in lista_analisis:
                categoria_detectada = cat_clave
                break
                
    if tipo_detectado == "Ingreso" and categoria_detectada == "Otros":
        categoria_detectada = "Otros Ingresos"
        if "salario" in texto or "sueldo" in texto: categoria_detectada = "Salario"
        if "inversion" in texto: categoria_detectada = "Inversiones"
        
    return fecha_detectada, tipo_detectado, categoria_detectada, monto_detectado

# ==========================================
# MOTOR DE RECOMENDACIONES IA (PRESCRIPTIVO)
# ==========================================
def generar_sugerencia_ia(categoria, monto_exceso):
    # Base de conocimientos heurística para simular análisis financiero avanzado
    estrategias = {
        "Alimentos": f"Se detectó un pico en consumo gastronómico. Recomendación IA: Suspende salidas a restaurantes durante los próximos 5 días y ejecuta compras programadas en formato 'hard discount' (D1, Ísimo). Esto compensará el exceso de ${monto_exceso:,.0f}.",
        "Transporte": f"Desviación en costos de movilidad. Recomendación IA: Consolida rutas de traslado, utiliza transporte multimodal o restringe el uso de plataformas (Uber/Didi) al mínimo operativo esta semana para reabsorber el sobregasto.",
        "Entretenimiento": f"Fuga de capital detectada en ocio. Recomendación IA: Aplica un congelamiento estricto en salidas recreativas los próximos dos fines de semana. Cancela temporalmente suscripciones activas de streaming que no uses para amortizar los ${monto_exceso:,.0f} excedidos.",
        "Tecnologia": f"Inversión de capital en activos tecnológicos por encima del promedio. Recomendación IA: Aplaza cualquier otra compra accesoria en hardware o licencias de software por este trimestre. Financia el excedente difiriendo gastos fijos no esenciales.",
        "Servicios Publicos": f"Pico en costos operativos del hogar. Recomendación IA: Auditoría de consumo eléctrico y optimización de planes de conectividad móvil o internet. Considera migrar a planes corporativos o empaquetados más eficientes.",
        "Otros": f"Desviación imprevista en caja. Recomendación IA: Ejecuta un ajuste del 10% en el presupuesto asignado a tus categorías variables durante lo que resta del mes para estabilizar el Flujo Neto."
    }
    return estrategias.get(categoria, estrategias["Otros"])

# ==========================================
# BARRA LATERAL: ENTRADA DE DATOS AI
# ==========================================
with st.sidebar:
    st.header("⚙️ Gestion de Activos")
    st.subheader("🎙️ Inteligencia de Voz AI")
    voice_input = st.text_input("Dictar transacción:", placeholder="Ej: Ayer gasté 45000 en gasolina", key="voice_input_field")
    
    if voice_input:
        fecha_v, tipo_v, cat_v, monto_v = procesar_comando_voz_avanzado(voice_input)
        st.markdown("### Datos Extraídos:")
        st.info(f"📅 **Fecha:** {fecha_v.strftime('%d/%m/%Y')}\n\n🔄 **Tipo:** {tipo_v}\n\n🏷️ **Categoría:** {cat_v}\n\n💵 **Monto:** ${monto_v:,.0f}")
        
        if st.button("Confirmar e Inyectar a Dashboard", use_container_width=True):
            if monto_v > 0:
                nueva_f = pd.DataFrame([[fecha_v, tipo_v, cat_v, voice_input, monto_v]], columns=st.session_state.transacciones.columns)
                st.session_state.transacciones = pd.concat([st.session_state.transacciones, nueva_f], ignore_index=True)
                st.success("Transacción indexada exitosamente.")
                st.rerun()

    st.markdown("---")
    with st.expander("➕ Registrar Manualmente"):
        tipo = st.radio("Tipo", ["Ingreso", "Gasto"])
        fecha = st.date_input("Fecha", datetime.date.today())
        lista_cats = CATEGORIAS_INGRESO if tipo == "Ingreso" else CATEGORIAS_GASTO
        cat = st.selectbox("Categoria", lista_cats)
        desc = st.text_input("Nota", "Detalle de operacion")
        monto = st.number_input("Monto ($)", min_value=0.0, step=50.0)
        
        if st.button("Confirmar Registro Manual", use_container_width=True):
            if monto > 0:
                nueva_f = pd.DataFrame([[fecha, tipo, cat, desc, monto]], columns=st.session_state.transacciones.columns)
                st.session_state.transacciones = pd.concat([st.session_state.transacciones, nueva_f], ignore_index=True)
                st.success("Dato indexado")
                st.rerun()

    with st.expander("🔧 Limites Presupuestarios"):
        for c in CATEGORIAS_GASTO:
            st.session_state.presupuestos[c] = st.number_input(f"{c}:", value=st.session_state.presupuestos[c], step=100.0)

# ==========================================
# CUERPO PRINCIPAL: DASHBOARD EJECUTIVO
# ==========================================
st.title("📈 Executive Finance Dashboard")
st.markdown("---")

c1, c2 = st.columns(2)
with c1: f_inicio = st.date_input("Desde", datetime.date.today() - datetime.timedelta(days=30))
with c2: f_fin = st.date_input("Hasta", datetime.date.today())

df = st.session_state.transacciones.copy()
if not df.empty:
    df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
    df = df[(df['Fecha'] >= f_inicio) & (df['Fecha'] <= f_fin)]

# KPIs Consolidados
ing = df[df['Tipo'] == "Ingreso"]['Monto'].sum()
gst = df[df['Tipo'] == "Gasto"]['Monto'].sum()
bal = ing - gst
tasa_ahorro = ((ing - gst) / ing * 100) if ing > 0 else 0

m1, m2, m3 = st.columns(3)
m1.metric("Ingresos Totales", f"${ing:,.0f}")
m2.metric("Gastos Totales", f"${gst:,.0f}")
m3.metric("Flujo Neto", f"${bal:,.0f}", delta=f"{tasa_ahorro:.1f}% Tasa Ahorro")

# --- SECCIÓN: ANÁLISIS DE TENDENCIA DIARIA CON ALERTA ---
st.markdown("### 📊 Analitica de Gastos Diarios e Insights IA")
df_gst = df[df['Tipo'] == "Gasto"] if not df.empty else pd.DataFrame()

# Calcular el límite diario global prorrateado (Suma de presupuestos mensuales / 30)
presupuesto_total_mensual = sum(st.session_state.presupuestos.values())
limite_diario_permitido = presupuesto_total_mensual / 30.0

if not df_gst.empty:
    df_diario = df_gst.groupby(['Fecha', 'Categoria'])['Monto'].sum().reset_index()
    df_diario = df_diario.sort_values(by="Fecha")
    
    # Construcción del gráfico con Plotly
    fig_diario = px.bar(
        df_diario, x='Fecha', y='Monto', color='Categoria',
        title=f"Evolucion Cronologica (Línea Roja: Alerta Diaria Global ${limite_diario_permitido:,.0f})",
        labels={'Monto': 'Total Gastado ($)', 'Fecha': 'Dia de Operacion'},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    # AGREGAR LÍNEA DE ALERTA AL GRÁFICO (Target Line Gerencial)
    fig_diario.add_shape(
        type="line", x0=df_diario['Fecha'].min(), x1=df_diario['Fecha'].max(),
        y0=limite_diario_permitido, y1=limite_diario_permitido,
        line=dict(color="Red", width=3, dash="dashdot"),
        name="Límite Diario"
    )
    
    fig_diario.update_layout(barmode='stack', xaxis_tickformat='%d %b', hovermode='x unified', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_diario, use_container_width=True)
    
    # 🧠 MOTOR DE SUGERENCIAS IA SENSENSIBLE AL CONTEXTO 
    # Identificar días donde la sumatoria superó la alerta diaria
    df_total_por_dia = df_gst.groupby('Fecha')['Monto'].sum().reset_index()
    dias_excedidos = df_total_por_dia[df_total_por_dia['Monto'] > limite_diario_permitido]
    
    if not dias_excedidos.empty:
        st.markdown("#### 🧠 Centro de Mitigacion y Recomendaciones IA")
        # Analizar el día con la desviación más crítica para asesorar
        dia_critico = dias_excedidos.sort_values(by="Monto", ascending=False).iloc[0]
        fecha_critica = dia_critico['Fecha']
        monto_total_critico = dia_critico['Monto']
        exceso = monto_total_critico - limite_diario_permitido
        
        # Encontrar el rubro principal culpable de ese día específico
        rubro_principal = df_gst[df_gst['Fecha'] == fecha_critica].sort_values(by="Monto", ascending=False).iloc[0]['Categoria']
        
        # Desplegar la sugerencia de IA en interfaz destacada
        sugerencia_texto = generar_sugerencia_ia(rubro_principal, exceso)
        
        st.markdown(f"""
        <div class="ai-box">
            <h4>⚠️ Desviación Crítica Detectada el {fecha_critica.strftime('%d/%m/%Y')}</h4>
            <p>El gasto consolidado alcanzó <b>${monto_total_critico:,.0f}</b>, superando tu tolerancia diaria de Alerta por un monto de <b>${exceso:,.0f}</b>.</p>
            <p><b>Análisis Semántico de IA:</b> El principal vector de fuga detectado en esta fecha fue el rubro de <b>{rubro_principal}</b>.</p>
            <hr style='border-color: #475569;'>
            <h5>💡 Plan de Compensación Financiera:</h5>
            <p>{sugerencia_texto}</p>
        </div>
        """, unsafe_allow_html=True)
        
else:
    st.info("Sin registros de gastos en el periodo seleccionado para generar la tendencia diaria.")

# --- SECCIÓN: COMPOSICIÓN ESTRUCTURAL ---
st.markdown("### Visualizacion Estructural de Resultados")
col_g1, col_g2 = st.columns(2)

with col_g1:
    if not df_gst.empty:
        fig_donut = px.pie(df_gst, values='Monto', names='Categoria', hole=0.5, 
                         title="Distribucion Consolidada de Gastos", color_discrete_sequence=px.colors.qualitative.Safe)
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(margin=dict(t=40, b=40, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Aun no hay gastos registrados.")

with col_g2:
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name='Ingresos', x=['Totales'], y=[ing], marker_color='#2ecc71'))
    fig_comp.add_trace(go.Bar(name='Gastos', x=['Totales'], y=[gst], marker_color='#e74c3c'))
    fig_comp.update_layout(title="Comparativa Consolidada de Flujos", barmode='group', height=330, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)

# CONTROL DE PRESUPUESTOS (ALERTAS POR CATEGORÍA)
st.markdown("### Control de Desviaciones (Alertas Mensuales)")
cols_alert = st.columns(4)
gastos_agrupados = df_gst.groupby('Categoria')['Monto'].sum().to_dict() if not df_gst.empty else {}

for i, cat in enumerate(CATEGORIAS_GASTO):
    spent = gastos_agrupados.get(cat, 0)
    limit = st.session_state.presupuestos[cat]
    percent = (spent / limit) if limit > 0 else 0
    
    with cols_alert[i % 4]:
        st.write(f"**{cat}**")
        st.progress(min(percent, 1.0))
        if percent >= 1.0:
            st.caption(f":red[${spent:,.0f} de ${limit:,.0f} ({percent*100:.1f}%) - Excedido]")
        elif percent >= 0.8:
            st.caption(f":orange[${spent:,.0f} de ${limit:,.0f} ({percent*100:.1f}%) - Riesgo]")
        else:
            st.caption(f":green[${spent:,.0f} de ${limit:,.0f} ({percent*100:.1f}%) - Controlado]")

# DETALLE DE OPERACIONES
st.markdown("---")
with st.expander("🔍 Auditoria de Movimientos"):
    if not df.empty:
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
    else:
        st.info("Sin registros indexados.")
