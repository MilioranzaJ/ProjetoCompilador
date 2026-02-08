import sys
import os
from parser.parser import Parser
from interpretador.interpretador import interpretar_codigo
from lexer.lexer import imprimir_tokens

def main():
    caminho_arquivo = os.path.join("entrada", "correto.php.txt")
    if not os.path.exists(caminho_arquivo):
        print(f"'{caminho_arquivo}' não foi encontrado.")
        return

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo_fonte = arquivo.read()
    
        imprimir_tokens(codigo_fonte)
        print("\ncompilando codigo...")

        
        analisador = Parser(codigo_fonte)
        resultado = analisador.analisar()
        
        if not resultado:
            print("\ncompilacao falhou")
            return
        
        print("\ncompilacao bem sucedida")
        
        codigo_intermediario = analisador.gerador.obter_codigo()
        caminho_codigo_objeto = os.path.join("saida", "codigo_objeto.txt")
        analisador.gerador.salvar_para_arquivo(caminho_codigo_objeto)
        print(f"codigo objeto salvo em: {caminho_codigo_objeto}")
        
        print("executando codigo intermedio")
        
        print("\nO programa agora será executado.")
        print("Se houver leituras (LEIT) sera necessario digitar valores\n")
        
        resposta = input("deseja executar o programa? (s/n): ").strip().lower()
        
        if resposta == 's':
            interpretar_codigo(caminho_codigo_objeto)
            print("\nexecucao finalizada")
        else:
            print("\nexecucao pulada pelo usuario")

    except Exception as e:
        print(f"\nocorreu um erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()