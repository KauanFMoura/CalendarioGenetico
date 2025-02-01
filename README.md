# Algoritmo Genético para Montagem de Grade Horária do Curso de Ciência da Computação

## Descrição

Este trabalho tem como objetivo a implementação de um algoritmo genético para montar a grade horária do curso de Ciência da Computação do campus Santa Helena, abrangendo os períodos do 1º ao 4º. O algoritmo deve garantir a distribuição das disciplinas de forma que não existam conflitos entre os horários de disciplinas que são pré-requisito e suas correspondentes, bem como evitar conflitos de horários dos professores, onde um professor não pode ministrar diferentes disciplinas no mesmo dia e horário.

## Escopo

O algoritmo genético desenvolvido deve seguir os seguintes requisitos:

- **Codificação dos Cromossomos**: Cada cromossomo representa uma possível solução para a grade horária, considerando as disciplinas e os horários disponíveis.
- **Restrições de Horário**: Não deve haver conflitos entre as disciplinas que são pré-requisito e suas disciplinas correspondentes.
- **Restrições de Professores**: Nenhum professor pode ministrar mais de uma disciplina no mesmo dia e horário.
- **Geração de Soluções**: O algoritmo deve ser capaz de gerar soluções viáveis para a grade horária considerando as restrições do curso e dos professores.
