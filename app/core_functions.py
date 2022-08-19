import numpy as np

def distance(a, b) -> float:
    """ Função para retornar a distância entre dois pontos.

    Args:
        a (list): lista com coordenadas que descreve um ponto.
        b (list): lista com coordenadas que descreve um ponto.

    Returns:
        float: Distância entre os dois pontos como parâmetro.
    """
    return abs(np.linalg.norm(a-b))