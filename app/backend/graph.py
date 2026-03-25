from strands.multiagent import GraphBuilder
from agents import create_buscador_agent, create_redactor_agent, create_revisor_agent


def check_search_results(state):
    """Función de condición para decidir si el redactor debe redactar o no."""
    if not state.get("buscador") or len(state["buscador"]) == 0:
        return False
    return True

def create_graph():
    """Crea el grafo de agentes para la generación de pliegos."""

    builder = GraphBuilder()

    agente_buscador = create_buscador_agent()
    agente_redactor = create_redactor_agent()
    agente_revisor = create_revisor_agent()

    builder.add_node(agente_buscador, "buscador")
    builder.add_node(agente_redactor, "redactor")
    builder.add_node(agente_revisor, "revisor")


    builder.add_edge("buscador", "redactor", condition=check_search_results)  # Solo pasa al redactor si el buscador encuentra algo relevante
    builder.add_edge("redactor", "revisor")


    builder.set_entry_point("buscador")
    builder.set_execution_timeout(600)
    builder.set_node_timeout(180)

    graph = builder.build()

    return graph