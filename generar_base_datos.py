"""
Generador de base de datos JSON con 500 candidatos para LinkenChamba
Incluye sistema de puntuación basado en red neuronal multicapa
"""
import json
import random
from faker import Faker
import numpy as np
from red_neuronal_puntuacion import calcular_puntuacion_puesto, PUESTOS

fake = Faker('es_MX')  # Generador de datos en español

# Opciones del cuestionario
HABILIDADES_PRACTICAS = [
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

HERRAMIENTAS = [
    "Computadora (Windows, Internet, email)",
    "Teléfono y sistemas de mensajería",
    "Caja registradora o punto de venta",
    "Herramientas básicas (martillo, destornillador, etc.)",
    "Equipo de cocina o restaurante",
    "Vehículo para entregas",
    "Ninguno de los anteriores, pero aprendo rápido"
]

AMBIENTES = [
    "Me gusta el movimiento y estar activo todo el día",
    "Prefiero trabajo tranquilo y organizado",
    "Disfruto interactuar con mucha gente",
    "Trabajo mejor concentrado en una sola tarea",
    "Me adapto fácilmente a cualquier ambiente"
]

ACTIVIDADES = [
    "Ayudar directamente a clientes o personas",
    "Crear o arreglar cosas con las manos",
    "Organizar y poner todo en orden",
    "Aprender cosas nuevas constantemente",
    "Resolver problemas prácticos inmediatos"
]

CONOCIMIENTOS = [
    "Matemáticas (hacer cuentas, medir, calcular precios)",
    "Lectura rápida y comprensión de instrucciones",
    "Escritura clara para llenar formatos o tomar notas",
    "Conceptos básicos de ventas o servicio al cliente",
    "Conocimiento de productos específicos (comida, ropa, materiales, etc.)",
    "Ninguna en particular, pero aprendo viendo y practicando"
]

NIVELES = ["Nada", "Básico", "Intermedio", "Avanzado"]

TIPOS_TRABAJO = [
    "Trabajo de medio tiempo (4-6 horas diarias)",
    "Trabajo de tiempo completo (8 horas)",
    "Trabajo por proyectos o temporal",
    "Aprendizaje o capacitación con salario básico",
    "Cualquier opción mientras pueda aprender y crecer"
]

LOGROS = [
    "Aprender un oficio o skill específico",
    "Tener un ingreso estable para mis gastos",
    "Ganar experiencia para mejor empleo después",
    "Desarrollarme dentro de esta empresa",
    "Descubrir en qué soy bueno profesionalmente"
]

REACCIONES = [
    "Pregunto a alguien con más experiencia",
    "Busco la solución yo mismo investigando",
    "Organizo la información para entender mejor",
    "Actúo inmediatamente con lo que sé",
    "Mantengo la calma y evalúo opciones"
]

DESTACA = [
    "Cuando hay que ayudar a otros a entenderse",
    "Cuando hay que encontrar errores o detalles",
    "Cuando hay que aprender algo nuevo rápido",
    "Cuando hay que mantener el orden en el caos",
    "Cuando hay que motivar al equipo",
    "No estoy seguro, necesito oportunidad para descubrirlo"
]

MOTIVACIONES = [
    "Necesidad económica inmediata",
    "Aprender y desarrollar habilidades",
    "Estabilidad y crecimiento a largo plazo",
    "Ambiente de trabajo positivo",
    "Todas las anteriores"
]

# Las funciones calcular_puntuacion_puesto y obtener_red_neuronal 
# ahora se importan desde red_neuronal_puntuacion.py

def generar_respuestas_aleatorias():
    """Genera respuestas aleatorias al cuestionario"""
    return {
        "habilidades_practicas": random.sample(HABILIDADES_PRACTICAS, k=random.randint(3, 5)),
        "herramientas": random.sample(HERRAMIENTAS, k=random.randint(2, 4)),
        "ambiente": random.choice(AMBIENTES),
        "actividades": random.sample(ACTIVIDADES, k=random.randint(1, 3)),
        "conocimientos": random.sample(CONOCIMIENTOS, k=random.randint(2, 4)),
        "niveles": {
            "Productividad": random.choice(NIVELES),
            "Organización": random.choice(NIVELES),
            "Atención clientes": random.choice(NIVELES),
            "Trabajo equipo": random.choice(NIVELES)
        },
        "tipo_trabajo": random.choice(TIPOS_TRABAJO),
        "logros": random.sample(LOGROS, k=random.randint(1, 3)),
        "reaccion": random.choice(REACCIONES),
        "destaca": random.sample(DESTACA, k=random.randint(1, 3)),
        "motivacion": random.choice(MOTIVACIONES),
        "unico": fake.text(max_nb_chars=200)
    }

def generar_candidato():
    """Genera un candidato completo con datos y respuestas"""
    respuestas = generar_respuestas_aleatorias()
    
    # Calcular puntuaciones para cada puesto
    puntuaciones = {}
    for puesto in PUESTOS.keys():
        puntuaciones[puesto] = calcular_puntuacion_puesto(respuestas, puesto)
    
    candidato = {
        "id": fake.uuid4(),
        "nombre": fake.name(),
        "email": fake.email(),
        "telefono": fake.phone_number(),
        "direccion": fake.address().replace('\n', ', '),
        "respuestas_cuestionario": respuestas,
        "puntuaciones": puntuaciones,
        "fecha_registro": fake.date_between(start_date='-1y', end_date='today').isoformat()
    }
    
    return candidato

def main():
    """Genera la base de datos con 500 candidatos usando red neuronal"""
    print("Inicializando red neuronal multicapa...")
    print("Generando base de datos con 500 candidatos...")
    candidatos = []
    
    for i in range(500):
        candidato = generar_candidato()
        candidatos.append(candidato)
        if (i + 1) % 50 == 0:
            print(f"   Generados {i + 1}/500 candidatos...")
    
    base_datos = {
        "version": "1.0",
        "total_candidatos": len(candidatos),
        "puestos_disponibles": list(PUESTOS.keys()),
        "metodo_puntuacion": "Red neuronal multicapa (3 capas: 55->30->15->5) - Todas las preguntas del cuestionario",
        "candidatos": candidatos
    }
    
    # Guardar en JSON
    with open("base_datos_candidatos.json", "w", encoding="utf-8") as f:
        json.dump(base_datos, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Base de datos generada exitosamente!")
    print(f"   Archivo: base_datos_candidatos.json")
    print(f"   Total de candidatos: {len(candidatos)}")
    print(f"   Metodo: Red neuronal multicapa")
    
    # Mostrar estadísticas
    print("\nEstadisticas de puntuaciones promedio (calculadas con red neuronal):")
    for puesto in PUESTOS.keys():
        puntuaciones = [c["puntuaciones"][puesto] for c in candidatos]
        promedio = np.mean(puntuaciones)
        maximo = np.max(puntuaciones)
        minimo = np.min(puntuaciones)
        print(f"   {puesto}:")
        print(f"      Promedio: {promedio:.2f}%")
        print(f"      Maximo: {maximo:.2f}%")
        print(f"      Minimo: {minimo:.2f}%")

if __name__ == "__main__":
    main()

