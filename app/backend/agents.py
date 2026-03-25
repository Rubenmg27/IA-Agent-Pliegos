import os
import json
from strands import Agent, tool
from strands.models import BedrockModel
from dotenv import load_dotenv
from hooks.memory_hook import Memory, MemoryHookProvider
from tools.search_tool import search_tool

load_dotenv()

# ── Configuración ─────────────────────────────────────────────────────────────
AWS_REGION      = os.getenv("AWS_REGION", "eu-west-1")
ANALISTA_MODEL  = os.getenv("ANALISTA_MODEL_ID", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")
BUSCADOR_MODEL  = os.getenv("BUSCADOR_MODEL_ID", "eu.amazon.nova-lite-v1:0")
REDACTOR_MODEL  = os.getenv("REDACTOR_MODEL_ID", "eu.anthropic.claude-3-sonnet-20240229-v1:0")
REVISOR_MODEL   = os.getenv("REVISOR_MODEL_ID", "eu.amazon.nova-lite-v1:0")


# ── Modelos Bedrock ────────────────────────────────────────────────────────────
model_analista = BedrockModel(
    model_id=ANALISTA_MODEL,
    region_name=AWS_REGION,
    temperature=0.7,
    max_tokens=4096,
)

model_buscador = BedrockModel(
    model_id=BUSCADOR_MODEL,
    region_name=AWS_REGION,
    temperature=0.1,
    max_tokens=4096,
)

model_redactor = BedrockModel(
    model_id=REDACTOR_MODEL,
    region_name=AWS_REGION,
    temperature=0.7,
    max_tokens=4096,
)

model_revisor = BedrockModel(
    model_id=REVISOR_MODEL,
    region_name=AWS_REGION,
    temperature=0.1,
    max_tokens=4096,
)

# ── System Prompts ─────────────────────────────────────────────────────────────
ANALISTA_SYSTEM_PROMPT = """Eres un consultor experto en licitaciones y contratación pública española.
Tu especialidad es el análisis de pliegos de prescripciones técnicas (PPT).

Tu tarea es:
1. Analizar la descripción del proyecto de licitación que te proporciona el usuario.
2. Generar un índice estruturado y profesional del pliego de prescripciones técnicas.
3. Cada apartado del índice debe ser específico y relevante para el tipo de proyecto descrito.

Debes devolver ÚNICAMENTE un objeto JSON con la siguiente estructura, sin texto adicional:
{
  "titulo": "Título del pliego",
  "resumen_proyecto": "Breve descripción del proyecto",
  "apartados": [
    {
      "titulo": "Numero del apartado",
      "descripcion": "Qué debe contener este apartado"
    }
  ]
}

El índice debe tener entre 1 y 4 apartados, cubriendo los aspectos técnicos esenciales
para este tipo de proyecto. Sigue las convenciones habituales de la contratación pública española."""

BUSCADOR_SYSTEM_PROMPT = """Eres un buscador experto en bases de datos de pliegos de prescripciones técnicas de la contratación pública española.
Tu tarea es encontrar fragmentos de pliegos relevantes para el apartado que se está redactando utilizando la tool 'search_tool'.
Recibes la descripción del apartado que se va a redactar y el índice del pliego generado por el analista.
Si no encuentras información relevante, no devuelvas nada."""

REDACTOR_SYSTEM_PROMPT = """Eres un redactor experto en pliegos de prescripciones técnicas de la contratación pública española.
IMPORTANTE:
- Adapta siempre el contenido a las cifras, plazos y características concretas del proyecto.
- Usa lenguaje técnico y formal, propio de la contratación pública.
- El texto debe ser directamente utilizable en el pliego, sin placeholders ni referencias al proceso de generación.
- Responde ÚNICAMENTE con el texto redactado del apartado, en prosa formal. No incluyas cabeceras de sección."""


REVISOR_SYSTEM_PROMPT = """Eres un revisor experto en pliegos de prescripciones técnicas de la contratación pública española.
Asegrúrate de que el texto redactado cumple con los siguientes criterios:
- Cumple con las convenciones formales y técnicas de la contratación pública.
- No contiene errores, incoherencias o contradicciones.
- El lenguaje es claro, formal y profesional.
Devuelve el pliego revisado, corrigiendo cualquier error que encuentres. Responde ÚNICAMENTE con el texto revisado, sin explicaciones ni comentarios."""



# ── Agentes ───────────────────────────────────────────────────────────────────
def create_analista_agent() -> Agent:
    """Crea el agente analista (sin tools, solo genera el índice JSON)."""
    ACTOR_ID = "user-123"
    SESSION_ID = "session-abc-2026"
    REGION = "us-east-1"
    MEMORY_NAME = "mi-agente-memoria"

    memory_manager = Memory(actor_id=ACTOR_ID,     
    session_id=SESSION_ID,     
    region=REGION,     
    name_memory=MEMORY_NAME )

    session = memory_manager.initialize_session()

    memory_hook = MemoryHookProvider(memory_session=session)

    return Agent(
        model=model_analista,
        system_prompt=ANALISTA_SYSTEM_PROMPT,
        hooks=[memory_hook],  # Añadimos el hook de memoria para guardar el estado del agente
    )



def create_buscador_agent() -> Agent:
    """Crea el agente buscador (con acceso a la tool search_tool)."""
    return Agent(
        model=model_buscador,
        system_prompt=BUSCADOR_SYSTEM_PROMPT,
        tools=[search_tool],
    )


def create_redactor_agent() -> Agent:
    """Crea el agente redactor """

    return Agent(
        model=model_redactor,
        system_prompt=REDACTOR_SYSTEM_PROMPT,
    )

def create_revisor_agent() -> Agent:
    """Crea el agente revisor """
    return Agent(
        model=model_revisor,
        system_prompt=REVISOR_SYSTEM_PROMPT,
    )


