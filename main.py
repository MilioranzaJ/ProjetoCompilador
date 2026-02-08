import sys
import os
from parser.parser import Parser
from interpretador.interpretador import interpretar_codigo

def main():
    caminho_arquivo = os.path.join("entrada", "correto.php.txt")
    if not os.path.exists(caminho_arquivo):
        print(f"'{caminho_arquivo}' não foi encontrado.")
        return

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo_fonte = arquivo.read()
    
        print("compilando codigo...")

        
        analisador = Parser(codigo_fonte)
        resultado = analisador.analisar()
        
        if not resultado:
            print("\ncompilacao falhou")
            return
        
        print("\ncompilacao bem sucedida")
        
        codigo_intermediario = analisador.gerador.obter_codigo()
        
        print("executando codigo intermedio")
        
        print("\nO programa agora será executado.")
        print("Se houver leituras (LEIT) sera necessario digitar valores\n")
        
        resposta = input("deseja executar o programa? (s/n): ").strip().lower()
        
        if resposta == 's':
            interpretar_codigo(codigo_intermediario)
            print("\nexecucao finalizada")
        else:
            print("\nexecucao pulada pelo usuario")

    except Exception as e:
        print(f"\nocorreu um erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()