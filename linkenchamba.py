"""
LinkenChamba - Plataforma de conexión entre candidatos y microempresas
Incluye cifrado RSA y sistema de correos electrónicos
"""
import streamlit as st
import json
import pandas as pd
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from red_neuronal_puntuacion import calcular_puntuaciones, PUESTOS

# ---------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------
st.set_page_config(
    page_title="LinkenChamba",
    layout="wide"
)

# Paleta de colores en azul
AZUL_FONDO = "#0f172a"
AZUL_PRIMARIO = "#1d4ed8"
AZUL_SECUNDARIO = "#3b82f6"
AZUL_CLARO = "#e0f2fe"
AZUL_OSCURO = "#1e3a8a"
BLANCO = "#ffffff"

st.markdown(
    f"""
    <style>
        .main {{
            background: linear-gradient(135deg, {AZUL_CLARO} 0%, #f0f9ff 100%);
        }}
        .titulo-principal {{
            color: {AZUL_PRIMARIO};
            text-align: center;
            font-size: 48px;
            font-weight: 900;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        .subtitulo {{
            color: {AZUL_FONDO};
            text-align: center;
            font-size: 20px;
            margin-bottom: 2rem;
            font-weight: 500;
        }}
        .stButton>button {{
            background-color: {AZUL_PRIMARIO};
            color: {BLANCO};
            border-radius: 8px;
            padding: 0.5rem 2rem;
            border: none;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .stButton>button:hover {{
            background-color: {AZUL_OSCURO};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .card {{
            background-color: {BLANCO};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }}
        .puntuacion-alta {{
            color: #10b981;
            font-weight: bold;
            font-size: 18px;
        }}
        .puntuacion-media {{
            color: #f59e0b;
            font-weight: bold;
            font-size: 18px;
        }}
        .puntuacion-baja {{
            color: #ef4444;
            font-weight: bold;
            font-size: 18px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="titulo-principal"> LinkenChamba</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitulo">Conectando talento con oportunidades en microempresas</div>',
    unsafe_allow_html=True
)

# ---------------------------
# FUNCIONES DE CIFRADO RSA
# ---------------------------
def generar_par_claves_rsa():
    """Genera un par de claves RSA"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def serializar_clave_publica(public_key):
    """Serializa la clave pública a formato PEM"""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode('utf-8')

def serializar_clave_privada(private_key):
    """Serializa la clave privada a formato PEM"""
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem.decode('utf-8')

def cifrar_datos(datos, public_key_pem):
    """Cifra datos usando una clave pública RSA"""
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8'),
        backend=default_backend()
    )
    datos_bytes = json.dumps(datos).encode('utf-8')
    encrypted = public_key.encrypt(
        datos_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode('utf-8')

def descifrar_datos(datos_cifrados, private_key_pem):
    """Descifra datos usando una clave privada RSA"""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    encrypted_bytes = base64.b64decode(datos_cifrados)
    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return json.loads(decrypted.decode('utf-8'))

# ---------------------------
# FUNCIONES DE CORREO
# ---------------------------
def enviar_correo(destinatario, asunto, cuerpo, es_html=False):
    """Envía un correo electrónico"""
    # Configuración del servidor SMTP (Gmail como ejemplo)
    # NOTA: El usuario debe configurar sus credenciales en las variables de entorno
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_usuario = os.getenv("EMAIL_USUARIO", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")
    
    if not email_usuario or not email_password:
        st.warning("⚠️ Configura las variables de entorno EMAIL_USUARIO y EMAIL_PASSWORD para enviar correos.")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = email_usuario
        msg['To'] = destinatario
        
        if es_html:
            msg.attach(MIMEText(cuerpo, 'html'))
        else:
            msg.attach(MIMEText(cuerpo, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_usuario, email_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Error al enviar correo: {str(e)}")
        return False

# ---------------------------
# FUNCIONES DE PUNTUACIÓN
# ---------------------------
# Las funciones de puntuación se importan desde red_neuronal_puntuacion.py
# Esto asegura que todos los candidatos (generados y nuevos) usen la misma red neuronal

# ---------------------------
# ESTADO INICIAL
# ---------------------------
if "base_datos" not in st.session_state:
    st.session_state.base_datos = {"candidatos": []}
    st.session_state.clave_publica = None
    st.session_state.clave_privada = None

if "manual_bytes" not in st.session_state:
    st.session_state.manual_bytes = None
    st.session_state.manual_nombre = None
    st.session_state.manual_tipo = None

# Inicializar claves RSA si no existen
if st.session_state.clave_publica is None:
    private_key, public_key = generar_par_claves_rsa()
    st.session_state.clave_privada = serializar_clave_privada(private_key)
    st.session_state.clave_publica = serializar_clave_publica(public_key)

# ---------------------------
# SIDEBAR: CARGA DE BASE DE DATOS
# ---------------------------
st.sidebar.title(" Configuración")

st.sidebar.markdown("**Cargar base de datos JSON**")
archivo_json = st.sidebar.file_uploader(
    "Sube tu archivo JSON de candidatos",
    type=["json"],
    key="json_candidatos"
)

if archivo_json is not None:
    try:
        contenido = json.load(archivo_json)
        if "candidatos" in contenido:
            st.session_state.base_datos = contenido
            st.sidebar.success(f"{len(contenido['candidatos'])} candidatos cargados.")
        else:
            st.sidebar.error("El JSON debe contener una clave 'candidatos'.")
    except Exception as e:
        st.sidebar.error(f"Error al leer el JSON: {e}")

# Cargar desde archivo local si existe
if os.path.exists("base_datos_candidatos.json"):
    try:
        with open("base_datos_candidatos.json", "r", encoding="utf-8") as f:
            contenido = json.load(f)
            if "candidatos" in contenido:
                st.session_state.base_datos = contenido
    except:
        pass

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total candidatos:** {len(st.session_state.base_datos.get('candidatos', []))}")

# ---------------------------
# SECCIÓN: SUBIR Y DESCARGAR MANUAL
# ---------------------------
st.markdown("### Manual para descargar")

col_manual1, col_manual2 = st.columns(2)

with col_manual1:
    manual_file = st.file_uploader(
        "Sube el manual (PDF, DOCX, etc.)",
        type=None,
        key="manual"
    )
    if manual_file is not None:
        st.session_state.manual_bytes = manual_file.read()
        st.session_state.manual_nombre = manual_file.name
        st.session_state.manual_tipo = manual_file.type or "application/octet-stream"
        st.success(f"Manual '{st.session_state.manual_nombre}' cargado correctamente.")

with col_manual2:
    if st.session_state.manual_bytes is not None:
        st.download_button(
            label=f"⬇Descargar manual: {st.session_state.manual_nombre}",
            data=st.session_state.manual_bytes,
            file_name=st.session_state.manual_nombre,
            mime=st.session_state.manual_tipo,
            key="descargar_manual"
        )
    else:
        st.info("Aún no se ha subido ningún manual para descargar.")

st.markdown("---")

# ---------------------------
# SECCIÓN: REGISTRO DE NUEVOS CANDIDATOS
# ---------------------------
st.markdown("### 👤 Registro de nuevos candidatos")

with st.expander("Formulario de registro", expanded=True):
    with st.form("form_nuevo_candidato"):
        st.markdown("#### Información personal")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo *")
            email = st.text_input("Correo electrónico *")
        with col2:
            telefono = st.text_input("Número de teléfono *")
            direccion = st.text_area("Dirección *")
        
        st.markdown("---")
        st.markdown("#### Cuestionario de habilidades")
        
        st.markdown("**SECCIÓN 1: HABILIDADES PRÁCTICAS**")
        
        st.markdown("**1. De estas tareas cotidianas, ¿cuáles sabes hacer con confianza? (Elige hasta 5)**")
        habilidades_opciones = [
            "Atender clientes en mostrador o por teléfono",
            "Manejar caja registradora y dar cambio",
            "Organizar archivos o productos en inventario",
            "Usar computadora para escribir documentos básicos",
            "Empacar productos y preparar pedidos",
            "Limpiar y mantener áreas de trabajo ordenadas",
            "Ayudar en preparación de productos o materiales",
            "Tomar mensajes y recados con claridad",
            "Resolver quejas simples de clientes",
            "Ayudar a compañeros con sus tareas cuando es necesario"
        ]
        habilidades_seleccionadas = st.multiselect(
            "Selecciona tus habilidades:",
            habilidades_opciones,
            max_selections=5
        )
        
        st.markdown("**2. ¿Qué tipo de herramientas o equipos sabes usar?**")
        herramientas_opciones = [
            "Computadora (Windows, Internet, email)",
            "Teléfono y sistemas de mensajería",
            "Caja registradora o punto de venta",
            "Herramientas básicas (martillo, destornillador, etc.)",
            "Equipo de cocina o restaurante",
            "Vehículo para entregas",
            "Ninguno de los anteriores, pero aprendo rápido"
        ]
        herramientas_seleccionadas = st.multiselect(
            "Selecciona las herramientas que sabes usar:",
            herramientas_opciones
        )
        
        st.markdown("---")
        st.markdown("**SECCIÓN 2: INTERESES Y PREFERENCIAS**")
        
        st.markdown("**3. ¿En qué tipo de ambiente te sientes más cómodo trabajando?**")
        ambiente = st.radio(
            "Elige una opción:",
            [
                "Me gusta el movimiento y estar activo todo el día",
                "Prefiero trabajo tranquilo y organizado",
                "Disfruto interactuar con mucha gente",
                "Trabajo mejor concentrado en una sola tarea",
                "Me adapto fácilmente a cualquier ambiente"
            ],
            key="ambiente_radio"
        )
        
        st.markdown("**4. ¿Qué tipo de actividades te motivan más?**")
        actividades_opciones = [
            "Ayudar directamente a clientes o personas",
            "Crear o arreglar cosas con las manos",
            "Organizar y poner todo en orden",
            "Aprender cosas nuevas constantemente",
            "Resolver problemas prácticos inmediatos"
        ]
        actividades_seleccionadas = st.multiselect(
            "Selecciona las actividades que te motivan:",
            actividades_opciones
        )
        
        st.markdown("---")
        st.markdown("**SECCIÓN 3: CONOCIMIENTOS BÁSICOS**")
        
        st.markdown("**5. ¿En qué áreas tienes conocimientos aunque sea básicos?**")
        conocimientos_opciones = [
            "Matemáticas (hacer cuentas, medir, calcular precios)",
            "Lectura rápida y comprensión de instrucciones",
            "Escritura clara para llenar formatos o tomar notas",
            "Conceptos básicos de ventas o servicio al cliente",
            "Conocimiento de productos específicos (comida, ropa, materiales, etc.)",
            "Ninguna en particular, pero aprendo viendo y practicando"
        ]
        conocimientos_seleccionados = st.multiselect(
            "Selecciona tus áreas de conocimiento:",
            conocimientos_opciones
        )
        
        st.markdown("**6. ¿Qué sabes sobre estos temas? (Marca según tu nivel)**")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            nivel_productividad = st.selectbox("Productividad:", ["Nada", "Básico", "Intermedio", "Avanzado"])
            nivel_organizacion = st.selectbox("Organización:", ["Nada", "Básico", "Intermedio", "Avanzado"])
        with col_n2:
            nivel_atencion = st.selectbox("Atención clientes:", ["Nada", "Básico", "Intermedio", "Avanzado"])
            nivel_equipo = st.selectbox("Trabajo equipo:", ["Nada", "Básico", "Intermedio", "Avanzado"])
        
        st.markdown("---")
        st.markdown("**SECCIÓN 4: ASPIRACIONES LABORALES**")
        
        st.markdown("**7. ¿Qué tipo de trabajo buscas principalmente?**")
        tipo_trabajo = st.radio(
            "Elige una opción:",
            [
                "Trabajo de medio tiempo (4-6 horas diarias)",
                "Trabajo de tiempo completo (8 horas)",
                "Trabajo por proyectos o temporal",
                "Aprendizaje o capacitación con salario básico",
                "Cualquier opción mientras pueda aprender y crecer"
            ],
            key="tipo_trabajo_radio"
        )
        
        st.markdown("**8. ¿Qué te gustaría lograr en los próximos 6 meses?**")
        logros_opciones = [
            "Aprender un oficio o skill específico",
            "Tener un ingreso estable para mis gastos",
            "Ganar experiencia para mejor empleo después",
            "Desarrollarme dentro de esta empresa",
            "Descubrir en qué soy bueno profesionalmente"
        ]
        logros_seleccionados = st.multiselect(
            "Selecciona tus objetivos:",
            logros_opciones
        )
        
        st.markdown("---")
        st.markdown("**SECCIÓN 5: HABILIDADES INTERFUNCIONALES**")
        
        st.markdown("**9. Cuando surge un problema inesperado, tu primera reacción es:**")
        reaccion = st.radio(
            "Elige una opción:",
            [
                "Pregunto a alguien con más experiencia",
                "Busco la solución yo mismo investigando",
                "Organizo la información para entender mejor",
                "Actúo inmediatamente con lo que sé",
                "Mantengo la calma y evalúo opciones"
            ],
            key="reaccion_radio"
        )
        
        st.markdown("**10. ¿En qué situaciones destacas naturalmente?**")
        destaca_opciones = [
            "Cuando hay que ayudar a otros a entenderse",
            "Cuando hay que encontrar errores o detalles",
            "Cuando hay que aprender algo nuevo rápido",
            "Cuando hay que mantener el orden en el caos",
            "Cuando hay que motivar al equipo",
            "No estoy seguro, necesito oportunidad para descubrirlo"
        ]
        destaca_seleccionados = st.multiselect(
            "Selecciona las situaciones en las que destacas:",
            destaca_opciones
        )
        
        st.markdown("---")
        st.markdown("**SECCIÓN 6: DISPONIBILIDAD Y MOTIVACIÓN**")
        
        st.markdown("**11. ¿Cuál es tu principal motivación para trabajar aquí?**")
        motivacion = st.radio(
            "Elige una opción:",
            [
                "Necesidad económica inmediata",
                "Aprender y desarrollar habilidades",
                "Estabilidad y crecimiento a largo plazo",
                "Ambiente de trabajo positivo",
                "Todas las anteriores"
            ],
            key="motivacion_radio"
        )
        
        st.markdown("**12. ¿Qué te hace único como candidato? (Respuesta abierta breve)**")
        unico = st.text_area("Escribe tu respuesta (máximo 3 líneas):", max_chars=300)
        
        enviado = st.form_submit_button("✅ Registrar candidato", use_container_width=True)
        
        if enviado:
            if not nombre or not email or not telefono or not direccion:
                st.error("❌ Por favor, completa todos los campos obligatorios (*).")
            else:
                # Preparar respuestas
                respuestas = {
                    "habilidades_practicas": habilidades_seleccionadas,
                    "herramientas": herramientas_seleccionadas,
                    "ambiente": ambiente,
                    "actividades": actividades_seleccionadas,
                    "conocimientos": conocimientos_seleccionados,
                    "niveles": {
                        "Productividad": nivel_productividad,
                        "Organización": nivel_organizacion,
                        "Atención clientes": nivel_atencion,
                        "Trabajo equipo": nivel_equipo
                    },
                    "tipo_trabajo": tipo_trabajo,
                    "logros": logros_seleccionados,
                    "reaccion": reaccion,
                    "destaca": destaca_seleccionados,
                    "motivacion": motivacion,
                    "unico": unico
                }
                
                # Calcular puntuaciones
                puntuaciones = calcular_puntuaciones(respuestas)
                
                # Crear candidato
                nuevo_candidato = {
                    "id": f"cand_{len(st.session_state.base_datos['candidatos']) + 1}",
                    "nombre": nombre,
                    "email": email,
                    "telefono": telefono,
                    "direccion": direccion,
                    "respuestas_cuestionario": respuestas,
                    "puntuaciones": puntuaciones,
                    "fecha_registro": datetime.now().isoformat()
                }
                
                # Cifrar datos sensibles
                datos_sensibles = {
                    "email": email,
                    "telefono": telefono,
                    "direccion": direccion
                }
                nuevo_candidato["datos_cifrados"] = cifrar_datos(
                    datos_sensibles,
                    st.session_state.clave_publica
                )
                
                # Agregar a la base de datos
                st.session_state.base_datos["candidatos"].append(nuevo_candidato)
                
                st.success(f"Candidato '{nombre}' registrado exitosamente!")
                st.balloons()
                
                # Mostrar puntuaciones
                st.markdown("#### 📊 Tus puntuaciones por puesto:")
                for puesto, puntuacion in puntuaciones.items():
                    if puntuacion >= 70:
                        st.markdown(f"**{puesto}:** <span class='puntuacion-alta'>{puntuacion}%</span>", unsafe_allow_html=True)
                    elif puntuacion >= 40:
                        st.markdown(f"**{puesto}:** <span class='puntuacion-media'>{puntuacion}%</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{puesto}:** <span class='puntuacion-baja'>{puntuacion}%</span>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# SECCIÓN: BÚSQUEDA Y CONTRATACIÓN
# ---------------------------
st.markdown("### Buscar candidatos para contratar")

if len(st.session_state.base_datos.get("candidatos", [])) == 0:
    st.info("Aún no hay candidatos en la base de datos. Registra candidatos usando el formulario superior.")
else:
    tab_buscar, tab_estadisticas = st.tabs(["🔍 Buscar candidatos", "📊 Estadísticas generales"])
    
    with tab_buscar:
        st.markdown("#### Selecciona el puesto que necesitas:")
        puesto_seleccionado = st.selectbox(
            "Puesto:",
            PUESTOS,
            key="puesto_busqueda"
        )
        
        # Filtrar candidatos por puntuación mínima
        puntuacion_minima = st.slider(
            "Puntuación mínima requerida:",
            min_value=0,
            max_value=100,
            value=50,
            step=5
        )
        
        # Obtener candidatos con mejor puntuación para el puesto
        candidatos_filtrados = []
        for cand in st.session_state.base_datos["candidatos"]:
            puntuacion = cand.get("puntuaciones", {}).get(puesto_seleccionado, 0)
            if puntuacion >= puntuacion_minima:
                candidatos_filtrados.append({
                    "candidato": cand,
                    "puntuacion": puntuacion
                })
        
        # Ordenar por puntuación descendente
        candidatos_filtrados.sort(key=lambda x: x["puntuacion"], reverse=True)
        
        if not candidatos_filtrados:
            st.warning(f"⚠️ No se encontraron candidatos con puntuación >= {puntuacion_minima}% para {puesto_seleccionado}.")
        else:
            st.success(f"✅ Se encontraron {len(candidatos_filtrados)} candidatos.")
            
            # Mostrar lista de candidatos
            for idx, item in enumerate(candidatos_filtrados[:10]):  # Mostrar top 10
                cand = item["candidato"]
                punt = item["puntuacion"]
                
                with st.expander(f"👤 {cand['nombre']} - Puntuación: {punt}%", expanded=(idx == 0)):
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.markdown(f"**📧 Correo:** {cand.get('email', 'N/A')}")
                        st.markdown(f"**📱 Teléfono:** {cand.get('telefono', 'N/A')}")
                        st.markdown(f"**📍 Dirección:** {cand.get('direccion', 'N/A')}")
                    
                    with col_info2:
                        st.markdown("**📊 Puntuaciones en otros puestos:**")
                        for otro_puesto, otra_punt in cand.get("puntuaciones", {}).items():
                            if otro_puesto != puesto_seleccionado:
                                st.write(f"- {otro_puesto}: {otra_punt}%")
                    
                    st.markdown("**Lo que me hace único:**")
                    st.write(cand.get("respuestas_cuestionario", {}).get("unico", "No especificado"))
                    
                    # Botón para contactar
                    st.markdown("---")
                    col_contact1, col_contact2 = st.columns(2)
                    
                    with col_contact1:
                        if st.button(f"📧 Enviar correo a {cand['nombre']}", key=f"email_{cand['id']}"):
                            asunto = f"Oportunidad laboral - {puesto_seleccionado}"
                            cuerpo = f"""
                            Hola {cand['nombre']},
                            
                            Hemos revisado tu perfil y nos interesa contactarte para una oportunidad como {puesto_seleccionado}.
                            
                            Tu puntuación para este puesto es: {punt}%
                            
                            Por favor, contáctanos para más información.
                            
                            Saludos,
                            Equipo LinkenChamba
                            """
                            if enviar_correo(cand['email'], asunto, cuerpo):
                                st.success("✅ Correo enviado exitosamente!")
                    
                    with col_contact2:
                        st.info(f"📱 Contacto directo: {cand.get('telefono', 'N/A')}")
    
    with tab_estadisticas:
        st.markdown("#### 📊 Estadísticas de la base de datos")
        
        candidatos = st.session_state.base_datos.get("candidatos", [])
        
        if candidatos:
            # Estadísticas por puesto
            st.markdown("**Distribución de puntuaciones promedio por puesto:**")
            stats_puestos = {}
            for puesto in PUESTOS:
                puntuaciones = [c.get("puntuaciones", {}).get(puesto, 0) for c in candidatos]
                if puntuaciones:
                    stats_puestos[puesto] = {
                        "promedio": sum(puntuaciones) / len(puntuaciones),
                        "maximo": max(puntuaciones),
                        "minimo": min(puntuaciones)
                    }
            
            df_stats = pd.DataFrame(stats_puestos).T
            df_stats.columns = ["Promedio", "Máximo", "Mínimo"]
            st.dataframe(df_stats.round(2), use_container_width=True)
            
            # Gráfico de barras
            st.bar_chart(df_stats["Promedio"])
            
            # Top candidatos por puesto
            st.markdown("**Top 5 candidatos por puesto:**")
            for puesto in PUESTOS:
                st.markdown(f"##### {puesto}")
                top_candidatos = sorted(
                    [(c, c.get("puntuaciones", {}).get(puesto, 0)) for c in candidatos],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                for cand, punt in top_candidatos:
                    st.write(f"- **{cand['nombre']}**: {punt}%")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #64748b; padding: 2rem;">'
    'LinkenChamba - Conectando talento con oportunidades | '
    '🔒 Datos protegidos con cifrado RSA'
    '</div>',
    unsafe_allow_html=True
)
