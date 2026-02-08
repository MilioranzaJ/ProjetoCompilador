class Interpretador:
    
    def __init__(self, codigo):
        self.C = codigo  
        self.D = [0.0] * 10000  
        self.i = 0   
        self.s = -1  
        self.b = 0   
        self.executando = False
        self.max_instrucoes = 100000 
        self.contador_instrucoes = 0
        
    def executar(self):
        print("\n" + "="*60)
        print("           executando codigo intermed")
        print("="*60)
        
        self.executando = True
        self.contador_instrucoes = 0
        
        while self.executando and self.contador_instrucoes < self.max_instrucoes:
            self.contador_instrucoes += 1
            
            if self.i < 0 or self.i >= len(self.C):
                print(f"\nendereco da instrucao invalido: {self.i}")
                break
            
            instrucao = self.C[self.i].strip()
            
            if not instrucao or instrucao == '0':
                self.i += 1
                continue 
            
            self.executar_instrucao(instrucao)
        
        if self.contador_instrucoes >= self.max_instrucoes:
            print(f"\nlimite de {self.max_instrucoes} instrucoes atingido")
        
        print("\n" + "="*60)
        print("           execucao finalizada")
        print("="*60)
    
    def executar_instrucao(self, instrucao):
        partes = instrucao.split()
        operacao = partes[0]
        args = partes[1:] if len(partes) > 1 else []
        
        if operacao == 'INPP':
            self.s = -1
            self.i += 1
        
        elif operacao == 'PARA':
            self.executando = False
        
        elif operacao == 'CRCT':
            k = float(args[0])
            self.s += 1
            self.D[self.s] = k
            self.i += 1
        
        elif operacao == 'CRVL':
            n = int(args[0])
            self.s += 1
            self.D[self.s] = self.D[n]
            self.i += 1
        
        elif operacao == 'SOMA':
            self.D[self.s - 1] = self.D[self.s - 1] + self.D[self.s]
            self.s -= 1
            self.i += 1
        
        elif operacao == 'SUBT':
            self.D[self.s - 1] = self.D[self.s - 1] - self.D[self.s]
            self.s -= 1
            self.i += 1
        
        elif operacao == 'MULT':
            self.D[self.s - 1] = self.D[self.s - 1] * self.D[self.s]
            self.s -= 1
            self.i += 1
        
        elif operacao == 'DIVI':
            if self.D[self.s] == 0:
                print("\ndivisao por zero!!!!!")
                self.executando = False
                return
            self.D[self.s - 1] = self.D[self.s - 1] / self.D[self.s]
            self.s -= 1
            self.i += 1
        
        elif operacao == 'INVE':
            self.D[self.s] = -self.D[self.s]
            self.i += 1
        
        elif operacao == 'CONJ':
            if self.D[self.s - 1] == 1 and self.D[self.s] == 1:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'DISJ':
            if self.D[self.s - 1] == 1 or self.D[self.s] == 1:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'NEGA':
            self.D[self.s] = 1.0 - self.D[self.s]
            self.i += 1
        
        elif operacao == 'CPME':
            if self.D[self.s - 1] < self.D[self.s]:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'CPMA':
            if self.D[self.s - 1] > self.D[self.s]:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'CPIG':
            if self.D[self.s - 1] == self.D[self.s]:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'CDES':
            if self.D[self.s - 1] != self.D[self.s]:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'CPMI':
            if self.D[self.s - 1] <= self.D[self.s]:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'CMAI':
            if self.D[self.s - 1] >= self.D[self.s]:
                self.D[self.s - 1] = 1.0
            else:
                self.D[self.s - 1] = 0.0
            self.s -= 1
            self.i += 1
        
        elif operacao == 'ARMZ':
            n = int(args[0])
            self.D[n] = self.D[self.s]
            self.s -= 1
            self.i += 1
        
        elif operacao == 'ALME':
            m = int(args[0])
            self.s += m
            self.i += 1
        
        elif operacao == 'DESM':
            m = int(args[0])
            self.s -= m
            self.i += 1
        
        elif operacao == 'DSVI':
            p = int(args[0])
            self.i = p
        
        elif operacao == 'DSVF':
            if self.D[self.s] == 0.0:
                p = int(args[0])
                self.i = p
            else:
                self.i += 1
            self.s -= 1
        
        elif operacao == 'LEIT':
            try:
                valor = float(input("digite um valor: "))
                self.s += 1
                self.D[self.s] = valor
            except ValueError:
                print("\nvalor invalido n pode usar 0.0")
                self.s += 1
                self.D[self.s] = 0.0
            self.i += 1
        
        elif operacao == 'IMPR':
            print(self.D[self.s])
            self.s -= 1
            self.i += 1
        
        elif operacao == 'PUSHER':
            e = int(args[0])
            self.s += 1
            self.D[self.s] = float(e)
            self.i += 1
        
        elif operacao == 'PARAM':
            n = int(args[0])
            self.s += 1
            self.D[self.s] = self.D[n]
            self.i += 1
        
        elif operacao == 'CHPR':
            p = int(args[0])
            self.i = p
        
        elif operacao == 'RTPR':
            endereco_retorno = int(self.D[self.s])
            self.s -= 1
            self.i = endereco_retorno
        
        else:
            print(f"\ninstrução desconhecida: {operacao}")
            self.executando = False
    
    def dump_pilha(self, n=10):
        print("\n--- TOPO DA PILHA ---")
        inicio = max(0, self.s - n + 1)
        for i in range(inicio, self.s + 1):
            marcador = " <-- TOPO" if i == self.s else ""
            print(f"D[{i}] = {self.D[i]}{marcador}")
        print("--------------------\n")


def interpretar_codigo(codigo_lista):
    if isinstance(codigo_lista, str):
        try:
            with open(codigo_lista, "r", encoding="utf-8") as arquivo:
                codigo_lista = [linha.strip() for linha in arquivo if linha.strip()]
        except FileNotFoundError:
            print(f"\narquivo de codigo objeto nao encontrado: {codigo_lista}")
            return None

    interpretador = Interpretador(codigo_lista)
    interpretador.executar()
    return interpretador