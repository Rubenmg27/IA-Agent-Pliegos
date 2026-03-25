# Dependencias
from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents import create_analista_agent
from backend.graph import create_graph

# Inicializa una instancia de la aplicación
app = FastAPI()


# Modelo de datos de entrada
class PromptRequest(BaseModel):
    prompt: dict


def parse_event(event):
    """
    Parse a streaming event from the agent and return formatted output
    """
    # Skip events that don't need to be displayed
    if any(key in event for key in ['init_event_loop', 'start', 'start_event_loop']):
        return ""

    # Text chunks from supervisor
    if 'data' in event and isinstance(event['data'], str):
        return event['data']


    # Handle text messages from the assistant
    if 'event' in event:
        event_data = event['event']

        # Beginning of a tool use
        if 'contentBlockStart' in event_data and 'start' in event_data['contentBlockStart']:
            if 'toolUse' in event_data['contentBlockStart']['start']:
                tool_info = event_data['contentBlockStart']['start']['toolUse']
                return f"\n\n[Executing: {tool_info['name']}]\n\n"

    return ""


analist = create_analista_agent()

generator = create_graph()


# Analizar requerimientos de usuario
@app.post("/v1/agent-anlist/", tags=["agente-analist"])
def chat_agent_analist(req: PromptRequest):
    ANALIST_PROMPT = f"""
    Genera un índice para una licitación técnica con los siguientes parámetros del proyecto:

    ### DATOS DEL PROYECTO
    - **Tipo de Licitación:** {req.prompt.get('tipo_proyecto')}
    - **Descripción Principal:** {req.prompt.get('descripcion')}
    - **Ubicación/Ámbito Territorial:** {req.prompt.get('localizacion')}

    ### ESPECIFICACIONES TÉCNICAS
    - **Características Clave:** {req.prompt.get('caracteristicas_tecnicas')}
    - **Presupuesto Estimado:** {req.prompt.get('presupuesto')}
    - **Plazo de Ejecución:** {req.prompt.get('plazo_ejecucion')}

    ### RESTRICCIONES DE SALIDA
    - **Idioma de redacción:** {req.prompt.get('lenguaje')}
    - **Extensión estimada:** {req.prompt.get('max_pages')} páginas (ajusta la profundidad de los apartados a esta extensión).

    Asegúrate de que el JSON resultante sea válido y siga estrictamente el esquema solicitado en tus instrucciones de sistema.
    """
    respuesta = analist(ANALIST_PROMPT)

    # try:
    #     texto = respuesta["message"]["content"][0]["text"]
    #     # texto = respuesta["response"][0]

    # except Exception:

    #     texto = str(respuesta)

    return {"respuesta": respuesta.structured_output}


# Generar pliego del último  infice en memoria
@app.post("/v1/agent-generator/", tags=["agente-generator"])
async def chat_agent_generator(req: PromptRequest):
    GENERATOR_PROMPT = f"""
        Redacta un pliego de contratación de una entidad pública española.
        Tiene que atender este índice de secciones y especificación del documento:
        {req.prompt["indice"]}
    """

    try:
        async for event in generator.stream_async(GENERATOR_PROMPT):
            text = parse_event(event)
            if text:
                yield text

        # texto = respuesta["response"][0]
    except Exception as e:
            # Handle errors gracefully in streaming context
            error_response = {"error": str(e), "type": "stream_error"}
            print(f"Streaming error: {error_response}")
            yield error_response


if __name__ == "__main__":
    import uvicorn
    # Ejecutar la aplicación con Uvicorn en el puerto 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)
