"""
Módulo compartido con la red neuronal para calcular puntuaciones de candidatos
Usado tanto en el generador de base de datos como en la aplicación Streamlit
"""
import numpy as np

# Simulación de red neuronal multicapa para calcular puntuaciones
class RedNeuronalPuntuacion:
    """Red neuronal multicapa simple para calcular puntuaciones de candidatos"""
    def __init__(self):
        # Pesos aleatorios inicializados (simulando una red entrenada)
        np.random.seed(42)
        # Capa de entrada: 55 características (todas las preguntas del cuestionario)
        # Capa oculta 1: 30 neuronas
        # Capa oculta 2: 15 neuronas
        # Capa de salida: 5 puestos
        self.W1 = np.random.randn(55, 30) * 0.1
        self.b1 = np.random.randn(30) * 0.1
        self.W2 = np.random.randn(30, 15) * 0.1
        self.b2 = np.random.randn(15) * 0.1
        self.W3 = np.random.randn(15, 5) * 0.1
        self.b3 = np.random.randn(5) * 0.1
    
    def sigmoid(self, x):
        """Función de activación sigmoide"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def forward(self, X):
        """Propagación hacia adelante"""
        # Normalizar entrada
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Capa oculta 1
        Z1 = np.dot(X, self.W1) + self.b1
        A1 = self.sigmoid(Z1)
        
        # Capa oculta 2
        Z2 = np.dot(A1, self.W2) + self.b2
        A2 = self.sigmoid(Z2)
        
        # Capa de salida
        Z3 = np.dot(A2, self.W3) + self.b3
        A3 = self.sigmoid(Z3)
        
        return A3[0] * 100  # Escalar a 0-100%
    
    def extraer_caracteristicas(self, respuestas):
        """Extrae características numéricas de las respuestas"""
        features = []
        
        # Habilidades prácticas (10 características binarias)
        habilidades_opciones = [
            "Atender clientes", "Manejar caja", "Organizar archivos",
            "Usar computadora", "Empacar productos", "Limpiar y mantener",
            "Ayudar en preparación", "Tomar mensajes", "Resolver quejas",
            "Ayudar a compañeros"
        ]
        for hab in habilidades_opciones:
            hab_seleccionadas = respuestas.get("habilidades_practicas", [])
            features.append(1 if any(hab.lower() in h.lower() for h in hab_seleccionadas) else 0)
        
        # Herramientas (7 características binarias)
        herramientas_opciones = [
            "Computadora", "Teléfono", "Caja registradora",
            "Herramientas básicas", "Equipo de cocina", "Vehículo",
            "aprendo rápido"
        ]
        herramientas_seleccionadas = respuestas.get("herramientas", [])
        for herr in herramientas_opciones:
            features.append(1 if any(herr.lower() in h.lower() for h in herramientas_seleccionadas) else 0)
        
        # Ambiente (5 características one-hot)
        ambiente = respuestas.get("ambiente", "")
        ambientes_opciones = [
            "movimiento", "tranquilo", "interactuar", "concentrado", "adapto"
        ]
        for amb in ambientes_opciones:
            features.append(1 if amb.lower() in ambiente.lower() else 0)
        
        # Actividades (5 características binarias)
        actividades_opciones = [
            "Ayudar directamente", "Crear o arreglar", "Organizar",
            "Aprender cosas nuevas", "Resolver problemas"
        ]
        actividades_seleccionadas = respuestas.get("actividades", [])
        for act in actividades_opciones:
            features.append(1 if any(act.lower() in a.lower() for a in actividades_seleccionadas) else 0)
        
        # Conocimientos (6 características binarias)
        conocimientos_opciones = [
            "Matemáticas", "Lectura rápida", "Escritura clara",
            "Conceptos básicos de ventas", "Conocimiento de productos", "aprendo viendo"
        ]
        conocimientos_seleccionados = respuestas.get("conocimientos", [])
        for con in conocimientos_opciones:
            features.append(1 if any(con.lower() in c.lower() for c in conocimientos_seleccionados) else 0)
        
        # Niveles de conocimiento (4 características: 0=Nada, 1=Básico, 2=Intermedio, 3=Avanzado)
        niveles = respuestas.get("niveles", {})
        nivel_map = {"Nada": 0, "Básico": 1, "Intermedio": 2, "Avanzado": 3}
        for tema in ["Productividad", "Organización", "Atención clientes", "Trabajo equipo"]:
            nivel = niveles.get(tema, "Nada")
            features.append(nivel_map.get(nivel, 0) / 3.0)  # Normalizar a 0-1
        
        # Tipo de trabajo (1 característica)
        tipo_trabajo = respuestas.get("tipo_trabajo", "")
        if tipo_trabajo:
            features.append(1 if "tiempo completo" in tipo_trabajo.lower() else 0.5)
        else:
            features.append(0.5)  # Valor por defecto
        
        # Logros (5 características binarias)
        logros_opciones = [
            "Aprender un oficio", "Ingreso estable", "Ganar experiencia",
            "Desarrollarme dentro", "Descubrir en qué soy bueno"
        ]
        logros_seleccionados = respuestas.get("logros", [])
        for logro in logros_opciones:
            features.append(1 if any(logro.lower() in l.lower() for l in logros_seleccionados) else 0)
        
        # Reacción (5 características one-hot)
        reaccion = respuestas.get("reaccion", "")
        reacciones_opciones = [
            "pregunto", "busco", "organizo", "actúo", "mantengo"
        ]
        for reac in reacciones_opciones:
            features.append(1 if reac.lower() in reaccion.lower() else 0)
        
        # Destaca (6 características binarias)
        destaca_opciones = [
            "ayudar a otros", "encontrar errores", "aprender algo nuevo",
            "mantener el orden", "motivar al equipo", "necesito oportunidad"
        ]
        destaca_seleccionados = respuestas.get("destaca", [])
        for dest in destaca_opciones:
            features.append(1 if any(dest.lower() in d.lower() for d in destaca_seleccionados) else 0)
        
        # Motivación (1 característica)
        motivacion = respuestas.get("motivacion", "")
        if motivacion:
            if "todas" in motivacion.lower():
                features.append(1.0)
            elif "aprender" in motivacion.lower():
                features.append(0.8)
            elif "estabilidad" in motivacion.lower():
                features.append(0.6)
            else:
                features.append(0.4)
        else:
            features.append(0.5)  # Valor por defecto
        
        # Asegurar que tenemos exactamente 55 características (ajustar si es necesario)
        # Si tenemos más, tomar las primeras 55; si menos, rellenar con 0
        if len(features) > 55:
            features = features[:55]
        elif len(features) < 55:
            features.extend([0.0] * (55 - len(features)))
        
        return features

# Definición de puestos y sus criterios de puntuación
PUESTOS = {
    "Atención a Clientes/Ventas": {
        "habilidades_practicas": ["Atender clientes", "Manejar caja", "Resolver quejas", "Tomar mensajes"],
        "ambiente": ["interactuar", "adapto"]
    },
    "Asistente Administrativo": {
        "habilidades_practicas": ["Organizar archivos", "Usar computadora", "Tomar mensajes"],
        "ambiente": ["tranquilo", "concentrado"]
    },
    "Operario de Producción": {
        "habilidades_practicas": ["Ayudar en preparación", "Empacar productos", "Limpiar y mantener"],
        "ambiente": ["movimiento", "adapto"]
    },
    "Ayudante General": {
        "habilidades_practicas": ["Empacar productos", "Limpiar y mantener", "Organizar archivos", "Ayudar a compañeros"],
        "ambiente": ["adapto", "movimiento"]
    },
    "Ayudante en cocina": {
        "habilidades_practicas": ["Ayudar en preparación", "Limpiar y mantener", "Empacar productos"],
        "ambiente": ["movimiento", "concentrado"]
    }
}

# Instancia global de la red neuronal
_red_neuronal = None

def obtener_red_neuronal():
    """Obtiene o crea la instancia de la red neuronal"""
    global _red_neuronal
    if _red_neuronal is None:
        _red_neuronal = RedNeuronalPuntuacion()
    return _red_neuronal

def calcular_puntuacion_puesto(respuestas, puesto):
    """Calcula la puntuación usando red neuronal multicapa"""
    red_neuronal = obtener_red_neuronal()
    
    # Extraer características
    features = red_neuronal.extraer_caracteristicas(respuestas)
    
    # Obtener todas las puntuaciones de la red neuronal
    puntuaciones_todas = red_neuronal.forward(features)
    
    # Mapear a puestos específicos
    puestos_lista = list(PUESTOS.keys())
    indice_puesto = puestos_lista.index(puesto)
    puntuacion = puntuaciones_todas[indice_puesto]
    
    # Ajustar basado en criterios específicos del puesto
    criterios = PUESTOS[puesto]
    ajuste = 0
    
    # Ajuste por habilidades específicas
    habilidades_seleccionadas = respuestas.get("habilidades_practicas", [])
    matches = sum(1 for hab in habilidades_seleccionadas 
                  if any(crit.lower() in hab.lower() for crit in criterios["habilidades_practicas"]))
    ajuste += matches * 3
    
    # Ajuste por ambiente
    ambiente = respuestas.get("ambiente", "")
    if any(crit.lower() in ambiente.lower() for crit in criterios["ambiente"]):
        ajuste += 5
    
    # Normalizar y limitar
    puntuacion_final = min(100, max(0, puntuacion + ajuste))
    return round(puntuacion_final, 2)

def calcular_puntuaciones(respuestas):
    """Calcula las puntuaciones para todos los puestos usando red neuronal"""
    puntuaciones = {}
    for puesto in PUESTOS.keys():
        puntuaciones[puesto] = calcular_puntuacion_puesto(respuestas, puesto)
    return puntuaciones

