import random


def torneio(cromossomo1, cromossomo2):
    """
    Realiza o torneio entre dois cromossomos
    :param cromossomo1: cromossomo 1
    :param cromossomo2: cromossomo 2
    :return: o melhor individuo
    """

    if cromossomo1.fitness > cromossomo2.fitness:
        return cromossomo1
    else:
        return cromossomo2


def roleta(cromossomo1, cromossomo2):
    """
    Realiza a selecao por roleta entre dois individuos
    :param cromossomo1:
    :param cromossomo2:
    :return: vencedor da roleta
    """

    soma_fitness = abs(cromossomo1.fitness) + abs(cromossomo2.fitness)

    if soma_fitness == 0:
        return cromossomo1

    prob_cromossomo1 = abs(cromossomo1.fitness) / soma_fitness

    if random.random() < prob_cromossomo1:
        return cromossomo1
    else:
        return cromossomo2
