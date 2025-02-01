import matplotlib.pyplot as plt


def plot_evolucao(fitness_best_values: list[float], fitness_worst_values: list[float], fitness_avg_values: list[float]):
    # Gerar as gerações
    generations = list(range(1, len(fitness_best_values) + 1))

    plt.figure(figsize=(12, 6))
    plt.plot(generations, fitness_best_values, linestyle='-', color='#2ca02c', label="Melhor Fitness",
             markersize=6)  # Verde
    plt.plot(generations, fitness_avg_values, linestyle='-', color='#1f77b4', label="Fitness Médio",
             markersize=6)  # Azul
    plt.plot(generations, fitness_worst_values, linestyle='-', color='#d62728', label="Pior Fitness",
             markersize=6)  # Vermelho

    plt.title("Evolução do Fitness ao Longo das Gerações", fontsize=16, fontweight='bold', color='#333333')
    plt.xlabel("Geração", fontsize=14, fontweight='bold', color='#555555')
    plt.ylabel("Fitness", fontsize=14, fontweight='bold', color='#555555')

    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(fontsize=12, color='#555555')
    plt.yticks(fontsize=12, color='#555555')

    plt.axhline(y=0, color='#FFD700', linestyle='--', linewidth=2, label='Objetivo')  # Amarelo escuro
    plt.legend(fontsize=12, loc='upper left')

    plt.tight_layout()
    plt.savefig("output/evolucao_fitness.png")  # Salva
