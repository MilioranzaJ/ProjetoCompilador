# Compilador
Projeto de compilador PHP ascendente para a matéria de projeto de compiladores, com geração de código intermediário para a MaqHipo e execução via interpretador.

## Objetivo
Implementar um compilador completo (léxico, sintático e semântico) que gere código intermediário compatível com a MaqHipo e permita a execução de programas da linguagem.

## Como executar
1. Abra o terminal na pasta Compilador.
2. Execute:
	 `python main.py`
3. O arquivo de entrada padrão é entrada/correto.php.txt.

## Estrutura do projeto
- lexer/: analisador léxico
- parser/: analisador sintático, semântico e gerador de código
- interpretador/: máquina virtual da MaqHipo
- entrada/: exemplos de programas fonte
- parser/saida/: tabelas ACTION/GOTO geradas

## Observações
- O interpretador solicita entradas quando encontra a instrução LEIT.
- Para trocar o arquivo de entrada, ajuste o caminho em main.py ou altere o conteúdo contido em correto.php.txt.
