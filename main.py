from genetico import Genetico
from func_aux.plot_grade import salvar_grade
from func_aux.plot_evolucao import plot_evolucao

if __name__ == '__main__':
    genetico = Genetico()
    (cromosomo, best_fitness, list_best_fitness, list_pior_fitness,
     list_median_fitness) = genetico.run(100, 500)

    for i in [1, 2, 3, 4, None]:
        salvar_grade(i, cromosomo.to01())

    plot_evolucao(list_best_fitness, list_pior_fitness, list_median_fitness)

