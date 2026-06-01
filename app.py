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
    .voice-box { background-color: #2e3440; padding: 15px; border-radius: 10px; color: white; text-align: center; }
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
# MOTOR NLP: PROCESAMIENTO DE VOZ A DATOS
# ==========================================
def procesar_texto_voz(texto):
    texto = texto.lower()
    
    # 1. Extraer el primer número que encuentre (Monto)
    numeros = re.findall(r'\d+', texto)
    monto_detectado = float(numeros[0]) if numeros else 0.0
    
    # 2. Determinar si es Ingreso o Gasto (por defecto Gasto)
    tipo_detectado = "Gasto"
    if any(palabra in texto for palabra in ["ingreso", "recibi", "pago", "salario", "gane", "sueldo"]):
        tipo_detectado = "Ingreso"
        
    # 3. Clasificación Semántica por Categorías
    categoria_detectada = "Otros"
    
    diccionario_semantico = {
        "Alimentos": ["comida", "almuerzo", "restaurante", "mercado", "supermercado", "cena", "cafe", "hamburguesa"],
        "Transporte": ["gasolina", "uber", "taxi", "bus", "peaje", "carro", "moto", "parqueadero"],
        "Vivienda": ["arriendo", "alquiler", "hipoteca", "reparacion", "muebles"],
        "Servicios Publicos": ["luz", "agua", "gas", "internet", "telefono", "celular", "servicios"],
        "Entretenimiento": ["cine", "fiesta", "bar", "cerveza", "concierto", "viaje", "paseo", "suscripcion", "netflix"],
        "Tecnologia": ["computador", "celular", "software", "pantalla", "audifonos", "gadget"],
        "Educacion": ["curso", "universidad", "colegio", "libro", "matricula", "seminario"]
    }
    
    lista_analisis = CATEGORIAS_INGRESO if tipo_detectado == "Ingreso" else CATEGORIAS_GASTO
    
    # Buscar coincidencias clave
    for cat_clave, palabras_asociadas in diccionario_semantico.items():
        if any(palabra in texto for palabra in palabras_asociadas):
            if cat_clave in lista_analisis:
                categoria_detectada = cat_clave
                break
                
    # Si es ingreso y no clasificó, asignar una por defecto
    if tipo_detectado == "Ingreso" and categoria_detectada == "Otros":
        categoria_detectada = "Otros Ingresos"
        if "salario" in texto or "sueldo" in texto: categoria_detectada = "Salario"
        if "inversion" in texto: categoria_detectada = "Inversiones"
        
    return tipo_detectado, categoria_detectada, monto_detectado

# ==========================================
# BARRA LATERAL: ENTRADA DE DATOS
# ==========================================
with st.sidebar:
    st.header("⚙️ Gestion de Activos")
    
    # --- COMPONENTE DISRUPTIVO: COMANDO DE VOZ ---
    st.subheader("🎙️ Registro por Voz AI")
    st.markdown("<small>Presiona el botón e indica tu transacción de forma natural.</small>", unsafe_allow_html=True)
    
    # Inyección de JavaScript nativo para captura de micrófono en el navegador
    from streamlit.components.v1 import html
    my_html = """
    <div style="text-align:center;">
        <button id="start-btn" style="background-color:#e74c3c; color:white; border:none; padding:12px 20px; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">
            🎤 Hablar Ahora
        </button>
        <p id="status" style="color:#888; font-size:12px; margin-top:5px;">Micrófono listo</p>
    </div>

    <script>
        const btn = document.getElementById('start-btn');
        const status = document.getElementById('status');
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.interimResults = false;
            
            btn.addEventListener('click', () => {
                recognition.start();
                btn.style.backgroundColor = '#2ecc71';
                btn.innerText = '🔴 Escuchando...';
                status.innerText = 'Habla ahora con claridad...';
            });
            
            recognition.onspeechend = () => {
                recognition.stop();
                btn.style.backgroundColor = '#e74c3c';
                btn.innerText = '🎤 Hablar Ahora';
            };
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                status.innerText = "Entendido: " + transcript;
                
                # Enviar el texto capturado de vuelta a Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: transcript
                }, '*');
            };
            
            recognition.onerror = (event) => {
                status.innerText = 'Error en reconocimiento: ' + event.error;
                btn.style.backgroundColor = '#e74c3c';
                btn.innerText = '🎤 Hablar Ahora';
            };
        } else {
            status.innerText = 'Tu navegador no soporta comandos de voz. Usa Chrome o Safari.';
            btn.disabled = true;
        }
    </script>
    """
    
    # Capturar la salida del componente HTML
    texto_escuchado = html(my_html, height=100)
    
    # Manejo del texto transcrito si el usuario habló
    voice_input = st.text_input("Texto procesado por Voz:", key="voice_output_text")
    
    # Truco de sincronización para procesar el texto enviado por JS
    if voice_input:
        tipo_v, cat_v, monto_v = procesar_texto_voz(voice_input)
        st.info(f"**Detectado:** {tipo_v} en *{cat_v}* por **${monto_v:,.0f}**")
        
        if st.button("Confirmar Transaccion de Voz", use_container_width=True):
            if monto_v > 0:
                nueva_f = pd.DataFrame([[datetime.date.today(), tipo_v, cat_v, voice_input, monto_v]], columns=st.session_state.transacciones.columns)
                st.session_state.transacciones = pd.concat([st.session_state.transacciones, nueva_f], ignore_index=True)
                st.success("Transacción por voz indexada con éxito.")
                st.rerun()
            else:
                st.error("No se detectó un monto numérico válido en el audio.")

    st.markdown("---")
    
    # --- REGISTRO MANUAL TRADICIONAL (RESPALDO) ---
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
                st.success("Dato indexado correctamente")
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

# --- KPIs ---
ing = df[df['Tipo'] == "Ingreso"]['Monto'].sum()
gst = df[df['Tipo'] == "Gasto"]['Monto'].sum()
bal = ing - gst
tasa_ahorro = ((ing - gst) / ing * 100) if ing > 0 else 0

m1, m2, m3 = st.columns(3)
m1.metric("Ingresos Totales", f"${ing:,.0f}")
m2.metric("Gastos Totales", f"${gst:,.0f}")
m3.metric("Flujo Neto", f"${bal:,.0f}", delta=f"{tasa_ahorro:.1f}% Tasa Ahorro")

st.markdown("### Visualizacion de Resultados")
col_g1, col_g2 = st.columns(2)

with col_g1:
    df_gst = df[df['Tipo'] == "Gasto"]
    if not df_gst.empty:
        fig_donut = px.pie(df_gst, values='Monto', names='Categoria', hole=0.5, 
                         title="Distribucion Gerencial de Gastos",
                         color_discrete_sequence=px.colors.qualitative.Safe)
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(margin=dict(t=40, b=40, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Aun no hay gastos registrados en este rango temporal.")

with col_g2:
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name='Ingresos', x=['Totales'], y=[ing], marker_color='#2ecc71'))
    fig_comp.add_trace(go.Bar(name='Gastos', x=['Totales'], y=[gst], marker_color='#e74c3c'))
    fig_comp.update_layout(title="Comparativa de Flujos", barmode='group', height=330, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)

# --- CONTROL DE PRESUPUESTOS ---
st.markdown("### Control de Desviaciones (Alertas)")
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

# --- DETALLE DE OPERACIONES ---
st.markdown("---")
with st.expander("🔍 Auditoria de Movimientos"):
    if not df.empty:
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
    else:
        st.info("Sin registros indexados.")
