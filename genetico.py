import json
import random
import time

from bitarray import bitarray
from collections import namedtuple

from func_aux.selecao import torneio, roleta
from func_aux.cross_over import um_ponto, dois_pontos, uniforme
from func_aux.plot_grade import salvar_grade
from func_aux.plot_evolucao import plot_evolucao


def ler_arquivo(path):
    with open(path, "r") as file:
        data = json.load(file)

    return data


class Genetico:

    def __init__(self):

        self.disciplinas = ler_arquivo("codigos/disciplinas.json")
        self.horarios = ler_arquivo("codigos/horarios.json")

        self.populacao = []
        self.cromossomo = namedtuple("Cromossomo", ["bits", "fitness"])

        self.vazio = []
        for key, value in self.disciplinas.items():
            if value[0] == "Vazio":
                self.vazio.append(key)

        self.total_aulas = 0
        for key, value in self.disciplinas.items():
            if value[0] != "Vazio":
                self.total_aulas += 1

        self.tam_aula = 0

        self.codigos_extras = {
            "110010": "000001",  # Extra: Segunda, 08h20
            "110011": "000011",  # Extra: Segunda, 10h20
            "110100": "001100",  # Extra: Terça, 09h10
            "110101": "010010",  # Extra: Terça, 15h50
            "110110": "010100",  # Extra: Quarta, 07h30
            "110111": "011001",  # Extra: Quarta, 16h40
            "111000": "010011",  # Extra: Quarta, 10h20
            "111001": "011110",  # Extra: Quinta, 07h30
            "111010": "100100",  # Extra: Quinta, 14h40
            "111011": "100111",  # Extra: Quinta, 16h40
            "111100": "101000",  # Extra: Sexta, 07h30
            "111101": "101001",  # Extra: Sexta, 08h20
            "111110": "101010",  # Extra: Sexta, 09h10
            "111111": "101111",  # Extra: Sexta, 14h40
        }

        self.dict_dias = {}
        for key, value in self.horarios.items():
            if key in self.codigos_extras:
                continue

            if value[0] in self.dict_dias:
                self.dict_dias[value[0]].append(key)
            else:
                self.dict_dias[value[0]] = [key]

        self.best_cromossomo = None
        self.best_fitness = float('-inf')
        self.fitness_best_list = []
        self.fitness_pior_list = []
        self.media_fitness = []

        self.horarios_manha = []
        self.horarios_tarde = []

        for key, value in self.horarios.items():
            if key in self.codigos_extras:
                continue

            if value[1] in ["07h30", "08h20", "09h10", "10h20", "11h10"]:
                self.horarios_manha.append(key)
            else:
                self.horarios_tarde.append(key)

    def gerar_populacao(self, tamanho_populacao: int):
        """
        Gera uma populacao de individuos
        :param tamanho_populacao: tamanho da populacao
        :return: lista de individuos
        """

        def gerar_cromossomo():
            """  Gera um cromossomo aleatorio """

            cromossomo = ""
            for _ in range(len(self.horarios)):
                for _ in range(2):  # duplicar horarios, para possibilitar mais de uma disciplina no mesmo horario
                    horario = list(self.horarios.keys())[random.randint(0, len(self.horarios) - 1)]
                    disciplina = list(self.disciplinas.keys())[random.randint(0, len(self.disciplinas) - 1)]

                    cromossomo += horario + disciplina
                    self.tam_aula = len(horario) + len(disciplina)  # tamanho da cadeia que representa uma aula

            return bitarray(cromossomo)

        for _ in range(tamanho_populacao):
            new_cromossomo = gerar_cromossomo()
            self.populacao.append(self.cromossomo(new_cromossomo, self.fitness(new_cromossomo)))

        return self.populacao

    def fitness(self, cromossomo: bitarray):
        """
        Funcao de avaliacao do cromossomo
        :param cromossomo: cromossomo a ser avaliado
        :return: fitness do cromossomo
        """

        fitness = 0
        dict_horarios = {}  # dicionario para armazenar as informacoes de cada horario
        for key, value in self.horarios.items():

            if key in self.codigos_extras:
                continue

            dict_horarios[key] = []  #

        count_horarios = {}  # dicionario para contar a quantidade de disciplinas em cada horario
        count_disciplinas = {}  # dicionario para contar a quantidade de disciplinas

        for i in range(0, len(cromossomo), self.tam_aula):

            disciplina = cromossomo[i + 6:i + 11].to01()

            if disciplina in self.vazio:  # disciplina vazia
                continue

            horario = cromossomo[i:i + 6].to01()
            if horario in self.codigos_extras:  # se for um horario extra, trocar pelo horario normal
                horario = self.codigos_extras[horario]

            # AVALIACAO DE HORARIOS (-5 PONTOS POR HORARIO COM MAIS DE 3 DISCIPLINAS)
            # =======================================================================
            count_horarios[horario] = count_horarios.setdefault(horario, 0) + 1
            if count_horarios[horario] > 3:
                fitness -= 1
            # =======================================================================

            # AVALIACAO DE DISCIPLINAS
            count_disciplinas[disciplina] = count_disciplinas.setdefault(disciplina, 0) + 1

            perido = self.disciplinas[disciplina][1]
            professor = self.disciplinas[disciplina][3]
            pre_requisito = self.disciplinas[disciplina][4]

            aula = [disciplina, perido, professor, pre_requisito]

            dict_horarios[horario].append(aula)  # adiciona a aula ao horario
        # AVALIACAO DE DISCIPLINAS (-20 POR DISICIPLINA A MAIS OU A MENOS, E -100 POR DISCIPLINA FALTANTE)
        # =======================================================================
        for key, value in count_disciplinas.items():
            fitness -= 100 * abs(self.disciplinas[key][2] - value)  # disciplina a mais ou a menos, penalidade

        fitness -= 1000 * (abs(len(count_disciplinas) - self.total_aulas))  # disciplina faltante, penalidade
        # =======================================================================
        # VERIFICAR SE EXISTEM DISCIPLINAS DO MESMO PERIODO/PRE-REQUISITOS/PROFESSORES EM HORARIOS IGUAIS (-20 PONTOS)
        # =======================================================================
        for horarios, aulas in dict_horarios.items():
            total_aulas = len(aulas)  # total de aulas no horario
            aulas_iguais = set()  # variavel que armazena valores unicos de aulas
            professores_iguais = set()  # variavel que armazena valores unicos de professores
            periodos_iguais = set()  # variavel que armazena valores unicos de periodos
            pre_requisitos = list()  # variavel que armazena os pre-requisitos

            for i in range(len(aulas)):
                aulas_iguais.add(aulas[i][0])  # adiciona a aula ao conjunto daquele horario
                periodos_iguais.add(aulas[i][1])  # adiciona o periodo ao conjunto daquele horario
                professores_iguais.add(aulas[i][2])  # adiciona o professor ao conjunto daquele horario
                pre_requisitos.append(aulas[i][3])  # adiciona o pre-requisito a lista daquele horario

            # Se aulas forem diferentes de total de aulas, entao tem aulas iguais no mesmo horario
            if len(aulas_iguais) != total_aulas:
                fitness -= 100 * abs(total_aulas - len(aulas_iguais))

            # Se periodos forem diferentes de total de aulas, entao tem periodos iguais no mesmo horario
            if len(periodos_iguais) != total_aulas:
                fitness -= 100 * abs(total_aulas - len(periodos_iguais))

            # Se professores forem diferentes de total de aulas, entao tem professores iguais no mesmo horario
            if len(professores_iguais) != total_aulas:
                fitness -= 100 * abs(total_aulas - len(professores_iguais))

            # Se tiver aula igual a um pre-requisto, entao tem aula e pre-requisito no mesmo horario
            if aulas_iguais.intersection(pre_requisitos):
                fitness -= 20 * len(aulas_iguais.intersection(pre_requisitos))
        # =======================================================================
        # AVALIACAO DE DISPERCAO DE AULAS IGUAIS (PREFEREIVEL AULAS SEQUENCIAS, POREM ATE 3)
        # =======================================================================

        for dia, horarios_all in self.dict_dias.items():
            for corte in range(0, len(horarios_all), 5):
                horarios = horarios_all[corte:corte + 5]

                aulas_por_periodo = []  # Lista para armazenar aulas por período

                # Coletar as aulas de cada período
                for horario in horarios:
                    if horario in dict_horarios:
                        aulas_do_horario = [aula[0] for aula in dict_horarios[horario]]  # Pegando o código da aula
                        aulas_por_periodo.append(aulas_do_horario)
                    else:
                        aulas_por_periodo.append([])  # Caso não tenha aula no horário

                # Contar aulas consecutivas
                contagem_aulas = []
                aula_anterior = {}

                for aulas in aulas_por_periodo:
                    contagem_atual = {}

                    for aula in aulas:
                        if aula in aula_anterior:
                            contagem_atual[aula] = aula_anterior[aula] + 1
                        else:
                            contagem_atual[aula] = 1

                    contagem_aulas.append(contagem_atual)
                    aula_anterior = contagem_atual  # Atualiza a referência para o próximo período

                contagem_fill = {}

                # Itera sobre cada dicionário na lista
                for dic in contagem_aulas:
                    for key, value in dic.items():
                        if key in contagem_fill:
                            contagem_fill[key] = max(contagem_fill[key], value)
                        else:
                            contagem_fill[key] = value

                # Exibe o resultado
                for i, contagem in enumerate([contagem_fill]):
                    for aula, duracao in contagem.items():
                        if duracao == 1:
                            fitness -= 1
                        elif duracao > 3:
                            fitness -= 1
                        else:
                            continue
        # =======================================================================

        # AVALIACAO DE HORARIOS DE AULAS (PREFEREIVEL AULAS DE MANHA EM PERIODO PAR E AULAS DE TARDE EM PERIODO IMPAR)
        # =======================================================================
        for key, value in dict_horarios.items():
            if key in self.horarios_manha:
                for aula in value:
                    if aula[0] == "10111":  # projeto Integrador inverte ao seu periodo
                        continue

                    if aula[1] % 2 != 0:
                        fitness -= 2
            else:
                for aula in value:
                    if aula[0] == "10111":
                        fitness -= 2
                        continue

                    if aula[1] % 2 == 0:
                        fitness -= 2
        # =======================================================================

        return fitness

    def selecao(self, taxa_selecao: float = 0.5, taxa_torneio: float = 0.8):
        """
        Realiza a selecao dos individuos
        :param taxa_selecao: taxa de individuos que serao selecionados
        :param taxa_torneio: taxa de individuos que serao selecionados por torneio
        :return: nova populacao de individuos
        """

        tamanho_selecao = int(len(self.populacao) * taxa_selecao)  # tamanho da selecao

        # realiza a selecao dos cromossomo em pares
        for _ in range(tamanho_selecao):

            cromossomo1 = self.populacao.pop(random.randint(0, len(self.populacao) - 1)) # seleciona um individuo aleatorio
            cromossomo2 = self.populacao.pop(random.randint(0, len(self.populacao) - 1))

            # Decidir se usa o torneio ou roleta com base nas taxas
            if random.random() < taxa_torneio:
                winner = torneio(cromossomo1, cromossomo2)  # realiza o torneio entre os individuos
            else:
                winner = roleta(cromossomo1, cromossomo2)  # realiza a selecao por roleta entre os individuos

            self.populacao.append(winner)

        return self.populacao

    def crossover(self, taxa_cross: float = 0.5, taxa_um_ponto: float = 0.5, taxa_dois_pontos: float = 0.3):
        """
        Realiza o crossover entre os cromossomos
        :param taxa_cross: quantidade de individuos que serao cruzados (a quantidade a mais sera o valor passado * 2)
        :param taxa_um_ponto: probabilidade de ocorrer o crossover de um ponto
        :param taxa_dois_pontos: probabilidade de ocorrer o crossover de dois pontos
        :return:
        """

        tamanho_cross = int(len(self.populacao) * taxa_cross)  # tamanho do crossover

        for _ in range(tamanho_cross):  # realiza o crossover entre os individuos
            pai1 = self.populacao[random.randint(0, len(self.populacao) - 1)].bits  # seleciona um individuo aleatorio
            pai2 = self.populacao[random.randint(0, len(self.populacao) - 1)].bits

            if random.random() < taxa_um_ponto:  # 50% de chance de ocorrer o crossover de um ponto
                filho1, filho2 = um_ponto(pai1, pai2)

            elif random.random() < (
                    taxa_um_ponto + taxa_dois_pontos):  # 30% de chance de ocorrer o crossover de dois pontos
                filho1, filho2 = dois_pontos(pai1, pai2)
            else:
                filho1, filho2 = uniforme(pai1, pai2)  # 20% de chance de ocorrer o crossover uniforme

            self.populacao.append(self.cromossomo(filho1, self.fitness(filho1)))
            self.populacao.append(self.cromossomo(filho2, self.fitness(filho2)))

        return self.populacao

    def mutacao(self, taxa_mutacao=0.05):
        """
        Realiza a mutacao de um individuo
        :param taxa_mutacao: taxa de mutacao
        :return:
        """
        tamanho_mutacao = int(len(self.populacao) * taxa_mutacao)

        for _ in range(tamanho_mutacao):
            cromossomo = self.populacao.pop(
                random.randint(0, len(self.populacao) - 1))  # seleciona um individuo aleatorio

            for i in range(len(cromossomo)):
                if random.random() < 0.60:  # 60% de chance de mutacao em cada gene
                    cromossomo.bits[i] = not cromossomo.bits[i]

            self.populacao.append(self.cromossomo(cromossomo.bits, self.fitness(cromossomo.bits)))

        return self.populacao

    def run(self, init_populacao: int = 10, num_geracoes: int = 10):
        """
        Executa o algoritmo genetico
        :param init_populacao: Tamanho da populacao inicial
        :param num_geracoes: Quantidade de geracoes
        :return: Melhor cromossomo e seu fitness, lista de fitness do melhor cromossomo, lista de fitness do pior
                cromossomo e lista de media dos fitness
        """

        self.gerar_populacao(init_populacao)  # gera a populacao inicial

        for i in range(num_geracoes):  # executa o algoritmo genetico
            start = time.time()  # tempo de inicio
            self.selecao()  # realiza a selecao
            self.crossover()  # realiza o crossover
            self.mutacao()  # realiza a mutacao

            media = 0
            pior = float('inf')

            for cromossomo in self.populacao:  # calcula o fitness de cada individuo
                media += cromossomo.fitness

                if cromossomo.fitness > self.best_fitness:  # verifica se o individuo é o melhor
                    self.best_fitness = cromossomo.fitness
                    self.best_cromossomo = cromossomo.bits

                if cromossomo.fitness < pior:  # verifica se o individuo é o pior
                    pior = cromossomo.fitness

            # armazena os valores de fitness
            self.fitness_best_list.append(self.best_fitness)
            self.fitness_pior_list.append(pior)
            media = round(media / len(self.populacao), 2)
            self.media_fitness.append(media)

            tempo = round(time.time() - start, 2)
            print(f"Geracao {i + 1} - População {len(self.populacao)} - Melhor Fitness: {self.best_fitness} "
                  f"- Pior Fitness: {pior} - Media dos Fitness: {media} - Tempo de Execução: {tempo}s")

        return self.best_cromossomo, self.best_fitness, self.fitness_best_list, self.fitness_pior_list, self.media_fitness
