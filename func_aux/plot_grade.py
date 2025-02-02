from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import json
import numpy as np


def ler_arquivo(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data


def gerar_grade(periodo_grade: int = None, bitarray: str = None):

    disciplinas_json = ler_arquivo("codigos/disciplinas.json")
    horarios_json = ler_arquivo("codigos/horarios.json")

    codigos_extras = {
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

    # Inicialização de uma tabela vazia de 5 dias úteis e 10 horários por dia
    dias_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    horarios_do_dia = ["07h30", "08h20", "09h10", "10h20", "11h10", "Almoço", "13h00", "13h50", "14h40", "15h50",
                       "16h40"]

    calendario = np.full((5, 11), "", dtype=object) # Inicializa com strings vazias

    for i in range(0, len(bitarray), 11): # Itera sobre os bits do cromossomo
        horario_bits = bitarray[i:i + 6]
        disciplina_bits = bitarray[i + 6:i + 11]

        if horario_bits in codigos_extras:
            horario_bits = codigos_extras[horario_bits]

        # Encontrar o horário e a disciplina
        dia, horario = horarios_json.get(horario_bits, ["", "Vazio"])
        nome_displina, periodo, _, professor, _, = disciplinas_json.get(disciplina_bits, ["Vazio"])

        if periodo_grade is None: # Se não for especificado um período, exibir todas as disciplinas
            disciplina = f"P{periodo} - {nome_displina} - {professor}"
        elif periodo_grade == periodo: # Se for especificado um período, exibir apenas as disciplinas daquele período
            disciplina = f"P{periodo} - {nome_displina} - {professor}"
        else:
            disciplina = ""

        if dia and horario and nome_displina != "Vazio":
            # Encontrar o índice do dia e do horário
            dia_idx = dias_da_semana.index(dia)
            horario_idx = horarios_do_dia.index(horario)

            # Adicionar a disciplina ao calendário
            calendario[dia_idx, horario_idx] += disciplina + "\n"

    return calendario, dias_da_semana


def salvar_grade(periodo_grade: int = None, bitarray: str = None):
    calendario, dias_da_semana = gerar_grade(periodo_grade, bitarray) # Gera a grade

    # Criando os intervalos de horários
    horarios_inicio = ["07h30", "08h20", "09h10", "10h20", "11h10", "13h00", "13h50", "14h40", "15h50", "16h40"]
    horarios_fim = ["08h20", "09h10", "10h20", "11h10", "12h00", "13h50", "14h40", "15h50", "16h40",
                    "17h30"]

    horarios_intervalo = [f"{inicio} - {fim}" for inicio, fim in zip(horarios_inicio, horarios_fim)]
    horarios_intervalo.insert(5, "Almoço")  # Insere 'almoço' nos horarios 

    data = [[""] * 6 for _ in range(len(horarios_intervalo) + 1)]  # Inicializa com strings vazias

    # Preenche os cabeçalhos
    data[0][0] = ""
    for j, horario in enumerate(horarios_intervalo):
        data[j + 1][0] = horario  # Adiciona os intervalos na primeira coluna

    for i, dia in enumerate(dias_da_semana):
        data[0][i + 1] = dia  # Adiciona os dias da semana na primeira linha

    # Preenche as células com as disciplinas
    for i in range(5):
        for j in range(len(horarios_intervalo)):
            data[j + 1][i + 1] = calendario[i, j]

    if periodo_grade is None:
        pdf_file = "output/grade_all.pdf"
    else:
        pdf_file = f"output/grade_{periodo_grade}.pdf"

    pdf = SimpleDocTemplate(pdf_file, pagesize=(1600, 850))

    tabela = Table(data)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  
        ('GRID', (0, 0), (-1, -1), 1, colors.black), 
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'), 
        ('FONTSIZE', (0, 0), (-1, -1), 10),  
        ('TOPPADDING', (0, 0), (-1, -1), 5),  
    ]))

    pdf.build([tabela])
