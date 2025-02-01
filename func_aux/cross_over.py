import random
import bitarray


def um_ponto(pai1, pai2):
    """
    Função que realiza o cruzamento de um ponto entre dois indivíduos.
    """
    ponto_corte = random.randint(0, len(pai1) - 1)

    filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
    filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]

    return filho1, filho2


def dois_pontos(pai1, pai2):
    """
    Função que realiza o cruzamento de dois pontos entre dois indivíduos.
    """

    ponto_corte1 = random.randint(0, len(pai1) - 1)
    ponto_corte2 = random.randint(0, len(pai1) - 1)

    if ponto_corte1 > ponto_corte2:
        ponto_corte1, ponto_corte2 = ponto_corte2, ponto_corte1

    filho1 = pai1[:ponto_corte1] + pai2[ponto_corte1:ponto_corte2] + pai1[ponto_corte2:]
    filho2 = pai2[:ponto_corte1] + pai1[ponto_corte1:ponto_corte2] + pai2[ponto_corte2:]

    return filho1, filho2


def uniforme(pai1, pai2):
    """
    Função que realiza o cruzamento uniforme entre dois indivíduos.
    """

    filho1 = bitarray.bitarray()

    for i in range(len(pai1)):
        if random.random() < 0.5:  # simula uma mascara de bits aleatória
            filho1.append(pai1[i])
        else:
            filho1.append(pai2[i])

    filho2 = ~filho1  # inverte os bits do filho1, para gerar o filho2

    return filho1, filho2
