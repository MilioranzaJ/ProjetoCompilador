import sys
import os

diretorio_parser = os.path.dirname(os.path.abspath(__file__))
diretorio_raiz = os.path.dirname(diretorio_parser)

if diretorio_raiz not in sys.path:
    sys.path.append(diretorio_raiz)
if diretorio_parser not in sys.path:
    sys.path.append(diretorio_parser)

from lexer.lexer import lexer 
from saida.tabelas import TABELA_ACTION, TABELA_GOTO, REGRAS_GRAMATICA


class Simbolo:
    def __init__(self, nome, categoria, escopo, linha, inicializada=False, parametros=None, end_rel=None):
        self.nome = nome
        self.categoria = categoria
        self.escopo = escopo
        self.linha = linha
        self.inicializada = inicializada
        self.parametros = parametros if parametros else []
        self.end_rel = end_rel
        self.prim_instr = None


class TabelaSimbolos:
    def __init__(self):
        self.escopos = {'global': {}}
        self.escopo_atual = 'global'
        self.contador_end_global = 0
        self.contador_por_escopo = {'global': 0}
        
    def entrar_escopo(self, nome_escopo):
        if nome_escopo not in self.escopos:
            self.escopos[nome_escopo] = {}
            self.contador_por_escopo[nome_escopo] = 0
        self.escopo_atual = nome_escopo
        
    def sair_escopo(self):
        self.escopo_atual = 'global'
        
    def inserir(self, simbolo):
        nome = simbolo.nome
        escopo = self.escopos[self.escopo_atual]
        
        if nome in escopo:
            return False
        
        escopo[nome] = simbolo
        return True
    
    def buscar(self, nome):
        if nome in self.escopos[self.escopo_atual]:
            return self.escopos[self.escopo_atual][nome]
        
        if self.escopo_atual != 'global':
            if nome in self.escopos['global']:
                return self.escopos['global'][nome]
        
        return None
    
    def buscar_funcao(self, nome):
        if nome in self.escopos['global']:
            simbolo = self.escopos['global'][nome]
            if simbolo.categoria == 'funcao':
                return simbolo
        return None
    
    def existe_no_escopo_atual(self, nome):
        return nome in self.escopos[self.escopo_atual]
    
    def obter_num_variaveis_locais(self, escopo=None):
        if escopo is None:
            escopo = self.escopo_atual
        return self.contador_por_escopo.get(escopo, 0)
    
    def imprimir(self):
        print("\n" + "="*60)
        print("              TABELA DE SIMBOLOS")
        print("="*60)
        
        for escopo, simbolos in self.escopos.items():
            if simbolos:
                print(f"\n[Escopo: {escopo}]")
                print("-"*40)
                for nome, simb in simbolos.items():
                    if simb.categoria == 'funcao':
                        params = ', '.join(simb.parametros) if simb.parametros else '(vazio)'
                        print(f"  {nome}: FUNCAO | Parametros: {params} | prim_instr: {simb.prim_instr}")
                    else:
                        status = "inicializada" if simb.inicializada else "nao inicializada"
                        print(f"  {nome}: VARIAVEL | {status} | end_rel: {simb.end_rel} | linha {simb.linha}")
        
        print("="*60 + "\n")


class GeradorCodigo:
    def __init__(self):
        self.codigo = []
        self.proxima_instrucao = 0
        
    def gerar(self, rotulo, arg1=None, arg2=None):
        if arg1 is not None and arg2 is not None:
            instrucao = f"{rotulo} {arg1} {arg2}"
        elif arg1 is not None:
            instrucao = f"{rotulo} {arg1}"
        else:
            instrucao = rotulo
        
        endereco = self.proxima_instrucao
        self.codigo.append(instrucao)
        self.proxima_instrucao += 1
        return endereco
    
    def obter_proximo_endereco(self):
        return self.proxima_instrucao
    
    def completar(self, endereco, rotulo, arg1=None, arg2=None):
        if arg1 is not None and arg2 is not None:
            self.codigo[endereco] = f"{rotulo} {arg1} {arg2}"
        elif arg1 is not None:
            self.codigo[endereco] = f"{rotulo} {arg1}"
        else:
            self.codigo[endereco] = rotulo
    
    def imprimir(self):
        print("\n" + "="*60)
        print("           CODIGO INTERMEDIARIO")
        print("="*60)
        for i, instrucao in enumerate(self.codigo):
            print(f"{i:6d}: {instrucao}")
        print("="*60 + "\n")
    
    def obter_codigo(self):
        return self.codigo


class Parser:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pilha = [0]
        self.pilha_valores = []
        self.linha_atual = 1

        self.tabela = TabelaSimbolos()
        self.erros_semanticos = []
        
        self.funcao_atual = None
        self.num_params_funcao_atual = 0
        
        self.gerador = GeradorCodigo()
        self.rotulos = {}
        
        self.pilha_controle = []
        
        self.dsvis_funcoes = []
        self.dsvis_corrigidos = False
        
        self.em_declaracao_variavel = False
        
        self.em_argumentos_funcao = False
        self.args_funcao_atual = []

        self.estados_declaracao_var = {2, 4, 16, 96}

    def corrigir_dsvis_funcoes(self):
        if not self.dsvis_corrigidos and self.dsvis_funcoes:
            end_main = self.gerador.obter_proximo_endereco()
            for dsvi_end in self.dsvis_funcoes:
                self.gerador.completar(dsvi_end, 'DSVI', end_main)
            self.dsvis_corrigidos = True

    def _deve_corrigir_dsvis_no_shift(self, estado_atual, lookahead):
        if self.dsvis_corrigidos or self.funcao_atual is not None:
            return False
        if lookahead in ('ECHO', 'IF', 'WHILE'):
            return True
        if lookahead == 'VAR':
            return estado_atual not in self.estados_declaracao_var
        if lookahead == 'IDENT':
            return estado_atual != 10
        return False

    def acao_semantica(self, regra, valores):        
        if regra == 'r1':
            #<programa> -> <?php <corpo> ?>
            return None
        
        elif regra == 'r8':
            #processar_declaracao_variavel
            return None
        
        elif regra == 'r9':
            #<atribuicao_opcional> -> = <expressao> ;
            return 'INICIALIZADA'
        
        elif regra == 'r10':
            #<atribuicao_opcional> -> ;
            return 'NAO_INICIALIZADA'
        
        elif regra == 'r11':
            #<dc_f> -> function ident <parametros> { <corpo_f> }
            num_locals = self.tabela.obter_num_variaveis_locais()
            num_total = self.num_params_funcao_atual + num_locals
            
            self.gerador.gerar('DESM', num_total)
            self.gerador.gerar('RTPR')
            
            self.tabela.sair_escopo()
            self.funcao_atual = None
            self.num_params_funcao_atual = 0
            return None
        
        elif regra == 'r12':
            #<parametros> -> ( <lista_par> )
            params = valores[1]
            if isinstance(params, list):
                for nome_param in params:
                    self.processar_parametro_funcao(nome_param)
            return params
        
        elif regra == 'r13':
            #<parametros> -> ( )
            return []
        
        elif regra == 'r14':
            #<lista_par> -> $ident <mais_par>
            param = valores[0]
            mais = valores[1] if valores[1] else []
            if isinstance(mais, list):
                return [param] + mais
            return [param]
        
        elif regra == 'r15':
            #<mais_par> -> , $ident <mais_par>
            param = valores[1]
            mais = valores[2] if valores[2] else []
            if isinstance(mais, list):
                return [param] + mais
            return [param]
        
        elif regra == 'r16':
            #<mais_par> -> λ
            return []
        
        elif regra == 'r25':
            #<comando> -> echo $ident . PHP_EOL ;
            nome_var = valores[1]
            simbolo = self.tabela.buscar(nome_var)
            
            if simbolo is None:
                self.erros_semanticos.append(
                    f"Linha {self.linha_atual}: Variável '{nome_var}' não declarada"
                )
            else:
                self.gerador.gerar('CRVL', simbolo.end_rel)
                self.gerador.gerar('IMPR')
            
            return None
        
        elif regra == 'r26':
            #<comando> -> if ( <condicao> ) { <comandos> } <pfalsa>
            info_if = self.pilha_controle.pop() if self.pilha_controle else None
            
            if info_if and info_if['tipo'] == 'if':
                if 'dsvi_else' in info_if:
                    end_atual = self.gerador.obter_proximo_endereco()
                    self.gerador.completar(info_if['dsvi_else'], 'DSVI', end_atual)
                else:
                    end_atual = self.gerador.obter_proximo_endereco()
                    self.gerador.completar(info_if['dsvf'], 'DSVF', end_atual)
            
            return None
        
        elif regra == 'r31':
            #<pfalsa> -> else { <comandos> }
            return 'TEM_ELSE'
        
        elif regra == 'r32':
            #<pfalsa> -> λ 
            return 'SEM_ELSE'
        
        elif regra == 'r27':
            #<comando> -> while ( <condicao> ) { <comandos> }
            info_while = self.pilha_controle.pop() if self.pilha_controle else None
            
            if info_while and info_while['tipo'] == 'while':
                self.gerador.gerar('DSVI', info_while['inicio'])
                end_atual = self.gerador.obter_proximo_endereco()
                self.gerador.completar(info_while['dsvf'], 'DSVF', end_atual)
            
            return None
        
        elif regra == 'r28':
            #<comando> -> $ident <restoIdent> ;
            nome_var = valores[0]
            resto = valores[1]
            
            if resto == 'ATRIBUICAO':
                simbolo = self.tabela.buscar(nome_var)
                if simbolo is None:
                    self.erros_semanticos.append(
                        f"Linha {self.linha_atual}: Variável '{nome_var}' não declarada"
                    )
                else:
                    simbolo.inicializada = True
                    self.gerador.gerar('ARMZ', simbolo.end_rel)
            
            return None
        
        elif regra == 'r29':
            #<restoIdent> -> = <expressao>
            return 'ATRIBUICAO'
        
        elif regra == 'r30':
            #<restoIdent> -> <lista_arg>
            return 'CHAMADA'
        
        elif regra == 'r40' or regra == 'r61':
            #<expressao> -> floatval(readline())
            self.gerador.gerar('LEIT')
            return None
        
        elif regra == 'r33':
            #<condicao> -> <expressao> <relacao> <expressao>
            operador = valores[1]
            
            if operador == '>':
                self.gerador.gerar('CPMA')
            elif operador == '<':
                self.gerador.gerar('CPME')
            elif operador == '>=':
                self.gerador.gerar('CMAI')
            elif operador == '<=':
                self.gerador.gerar('CPMI')
            elif operador == '==':
                self.gerador.gerar('CPIG')
            elif operador == '!=':
                self.gerador.gerar('CDES')
            
            end_dsvf = self.gerador.gerar('DSVF', 0)
            
            tipo_controle = 'if'
            inicio_while = None
            
            for info in reversed(self.pilha_controle):
                if info.get('tipo') == 'marcador_while':
                    tipo_controle = 'while'
                    inicio_while = info['inicio']
                    self.pilha_controle.remove(info)
                    break
            
            if tipo_controle == 'while':
                self.pilha_controle.append({
                    'tipo': 'while',
                    'dsvf': end_dsvf,
                    'inicio': inicio_while
                })
            else:
                self.pilha_controle.append({
                    'tipo': 'if',
                    'dsvf': end_dsvf
                })
            
            return None
        
        elif regra == 'r41':
            #<expressao> -> <termo> <outros_termos>
            return None
        
        elif regra == 'r42':
            #<outros_termos> -> <op_ad> <termo> <outros_termos>
            operador = valores[0]
            
            if operador == '+':
                self.gerador.gerar('SOMA')
            elif operador == '-':
                self.gerador.gerar('SUBT')
            
            return None
        
        elif regra == 'r43':
            #<outros_termos> -> λ
            return None
        
        elif regra == 'r46':
            #<termo> -> <op_un> <fator> <mais_fatores>
            if valores[0] == '-':
                self.gerador.gerar('INVE')
            return None
        
        elif regra == 'r47':
            #<op_un> -> -
            return '-'
        
        elif regra == 'r48':
            #<op_un> -> λ
            return None
        
        elif regra == 'r49':
            #<mais_fatores> -> <op_mul> <fator> <mais_fatores>
            operador = valores[0]
            
            if operador == '*':
                self.gerador.gerar('MULT')
            elif operador == '/':
                self.gerador.gerar('DIVI')
            
            return None
        
        elif regra == 'r50':
            #<mais_fatores> -> λ
            return None
        
        elif regra == 'r53':
            #<fator> -> $ident
            nome_var = valores[0]
            simbolo = self.tabela.buscar(nome_var)
            
            if simbolo is None:
                self.erros_semanticos.append(
                    f"Linha {self.linha_atual}: Variável '{nome_var}' não declarada (em expressão)"
                )
                return None
            
            if self.em_argumentos_funcao:
                self.args_funcao_atual.append(nome_var)
            else:
                self.gerador.gerar('CRVL', simbolo.end_rel)
            
            return nome_var
        
        elif regra == 'r54':
            #<fator> -> numero_real
            numero = valores[0]
            if not self.em_declaracao_variavel:
                self.gerador.gerar('CRCT', numero)
            return numero
        
        elif regra == 'r55':
            #<fator> -> ( <expressao> )
            return None
        
        elif regra == 'r56':
            #<lista_arg> -> ( <argumentos> )
            return valores[1]
        
        elif regra == 'r57':
            #<lista_arg> -> ( )
            return []
        
        elif regra == 'r58':
            #<argumentos> -> <expressao> <mais_ident>
            mais = valores[1] if valores[1] else []
            if isinstance(mais, list):
                return [valores[0]] + mais
            return [valores[0]]
        
        elif regra == 'r59':
            #<mais_ident> -> , <expressao> <mais_ident>
            mais = valores[2] if valores[2] else []
            if isinstance(mais, list):
                return [valores[1]] + mais
            return [valores[1]]
        
        elif regra == 'r60':
            #<mais_ident> -> λ
            return []
        
        elif regra == 'r62':
            #<comando> -> IDENT <lista_arg> ;
            nome_func = valores[0]
            
            self.em_argumentos_funcao = False
            args = self.args_funcao_atual.copy()
            self.args_funcao_atual = []
            
            simbolo_func = self.tabela.buscar_funcao(nome_func)
            if simbolo_func is None:
                self.erros_semanticos.append(
                    f"Linha {self.linha_atual}: Função '{nome_func}' não declarada"
                )
            else:
                num_esperado = len(simbolo_func.parametros)
                num_recebido = len(args)
                
                if num_esperado != num_recebido:
                    self.erros_semanticos.append(
                        f"Linha {self.linha_atual}: Função '{nome_func}' espera {num_esperado} argumento(s), recebeu {num_recebido}"
                    )
                
                end_retorno = self.gerador.obter_proximo_endereco() + num_recebido + 2
                self.gerador.gerar('PUSHER', end_retorno)
                
                for arg_nome in args:
                    simbolo_arg = self.tabela.buscar(arg_nome)
                    if simbolo_arg:
                        self.gerador.gerar('PARAM', simbolo_arg.end_rel)
                
                self.gerador.gerar('CHPR', simbolo_func.prim_instr)
            
            return None
        
        else:
            return valores[0] if valores else None
    
    def _esta_em_while(self):
        for item in reversed(self.pilha):
            if item == 'WHILE' or item == 'while':
                return True
            if item == 'IF' or item == 'if':
                return False
        return False
    
    def processar_declaracao_variavel(self, nome_var, inicializada):
        if self.tabela.existe_no_escopo_atual(nome_var):
            if inicializada == 'INICIALIZADA':
                simbolo = self.tabela.buscar(nome_var)
                if simbolo:
                    self.gerador.gerar('ARMZ', simbolo.end_rel)
            return
        
        if self.tabela.escopo_atual == 'global':
            end_rel = self.tabela.contador_end_global
            self.tabela.contador_end_global += 1
        else:
            num_globals = self.tabela.contador_end_global
            end_rel = num_globals + 1 + self.num_params_funcao_atual + self.tabela.contador_por_escopo[self.tabela.escopo_atual]
        
        self.tabela.contador_por_escopo[self.tabela.escopo_atual] += 1
        
        simbolo = Simbolo(
            nome=nome_var,
            categoria='variavel',
            escopo=self.tabela.escopo_atual,
            linha=self.linha_atual,
            inicializada=(inicializada == 'INICIALIZADA'),
            end_rel=end_rel
        )
        self.tabela.inserir(simbolo)
        
        self.gerador.gerar('ALME', 1)
        
    def processar_declaracao_funcao(self, nome_funcao):
        self.funcao_atual = nome_funcao
        self.num_params_funcao_atual = 0
        
        if self.tabela.buscar_funcao(nome_funcao):
            self.erros_semanticos.append(
                f"Linha {self.linha_atual}: Função '{nome_funcao}' já declarada"
            )
        else:
            end_dsvi = self.gerador.gerar('DSVI', 0)
            self.dsvis_funcoes.append(end_dsvi)
            
            end_inicio = self.gerador.obter_proximo_endereco()
            
            simbolo = Simbolo(
                nome=nome_funcao,
                categoria='funcao',
                escopo='global',
                linha=self.linha_atual,
                parametros=[]
            )
            simbolo.prim_instr = end_inicio
            self.tabela.inserir(simbolo)
            
            self.rotulos[nome_funcao] = {
                'dsvi': end_dsvi,
                'inicio': end_inicio
            }
        
        self.tabela.entrar_escopo(nome_funcao)
    
    def processar_parametro_funcao(self, nome_param):
        if self.funcao_atual:
            simbolo_func = self.tabela.buscar_funcao(self.funcao_atual)
            if simbolo_func and nome_param not in simbolo_func.parametros:
                simbolo_func.parametros.append(nome_param)
            
            if not self.tabela.existe_no_escopo_atual(nome_param):
                num_globals = self.tabela.contador_end_global
                end_rel = num_globals + 1 + self.num_params_funcao_atual
                
                simbolo_param = Simbolo(
                    nome=nome_param,
                    categoria='variavel',
                    escopo=self.tabela.escopo_atual,
                    linha=self.linha_atual,
                    inicializada=True,
                    end_rel=end_rel
                )
                self.tabela.inserir(simbolo_param)
                self.num_params_funcao_atual += 1
    
    def analisar(self):
        print(f"\nanalise e geracao do codigo")
        
        self.gerador.gerar('INPP')
        
        lexer.input(self.codigo)
        
        token_atual = lexer.token()
        lookahead = token_atual.type if token_atual else '$'
        valor_lookahead = token_atual.value if token_atual else 'EOF'
        self.linha_atual = token_atual.lineno if token_atual else 1
        
        while True:
            estado_atual = self.pilha[-1]
            acao = TABELA_ACTION.get((estado_atual, lookahead))
            
            if acao is None:
                self.erro_sintatico(estado_atual, lookahead, valor_lookahead)
                return False
            
            if acao.startswith('s'):
                proximo_estado = int(acao[1:])

                if self._deve_corrigir_dsvis_no_shift(estado_atual, lookahead):
                    self.corrigir_dsvis_funcoes()
                
                if estado_atual == 10 and lookahead == 'IDENT':
                    self.processar_declaracao_funcao(valor_lookahead)
                
                if lookahead == 'WHILE':
                    self.pilha_controle.append({
                        'tipo': 'marcador_while',
                        'inicio': self.gerador.obter_proximo_endereco()
                    })
                
                if lookahead == 'VAR' and estado_atual in self.estados_declaracao_var:
                    if not self.tabela.existe_no_escopo_atual(valor_lookahead):
                        self.em_declaracao_variavel = True
                    else:
                        self.em_declaracao_variavel = False
                elif lookahead == 'VAR':
                    self.em_declaracao_variavel = False
                
                if lookahead == 'ABRE_P' and estado_atual == 112:
                    self.em_argumentos_funcao = True
                    self.args_funcao_atual = []
                
                if lookahead == 'ELSE':
                    if self.pilha_controle:
                        info_if = self.pilha_controle[-1]
                        if info_if.get('tipo') == 'if':
                            dsvi_else = self.gerador.gerar('DSVI', 0)
                            end_else_inicio = self.gerador.obter_proximo_endereco()
                            self.gerador.completar(info_if['dsvf'], 'DSVF', end_else_inicio)
                            info_if['dsvi_else'] = dsvi_else
                
                self.pilha.append(valor_lookahead)
                self.pilha.append(proximo_estado)
                self.pilha_valores.append(valor_lookahead)
                
                token_atual = lexer.token()
                lookahead = token_atual.type if token_atual else '$'
                valor_lookahead = token_atual.value if token_atual else 'EOF'
                if token_atual:
                    self.linha_atual = token_atual.lineno
            
            elif acao.startswith('r'):
                regra_id = acao
                nome_nt, qtd_filhos = REGRAS_GRAMATICA[regra_id]
                
                valores_filhos = []
                if qtd_filhos > 0:
                    valores_filhos = self.pilha_valores[-qtd_filhos:]
                    self.pilha_valores = self.pilha_valores[:-qtd_filhos]
                
                if not self.dsvis_corrigidos and self.funcao_atual is None:
                    if nome_nt in ('comando', 'comandos'):
                        self.corrigir_dsvis_funcoes()
                
                if regra_id == 'r8':
                    nome_var = valores_filhos[0]
                    inicializacao = valores_filhos[1]
                    self.em_declaracao_variavel = False
                    self.processar_declaracao_variavel(nome_var, inicializacao)
                    resultado_semantico = None
                
                else:
                    resultado_semantico = self.acao_semantica(regra_id, valores_filhos)
                
                self.pilha_valores.append(resultado_semantico)
                
                if qtd_filhos > 0:
                    for _ in range(qtd_filhos * 2):
                        self.pilha.pop()
                
                estado_topo = self.pilha[-1]
                nt_limpo = nome_nt.replace('<', '').replace('>', '')
                proximo_estado_goto = TABELA_GOTO.get((estado_topo, nt_limpo))
                
                if proximo_estado_goto is None:
                    print(f"[erro na tabela goto] Estado {estado_topo} não tem transição para {nt_limpo}")
                    return False
                
                self.pilha.append(nome_nt)
                self.pilha.append(proximo_estado_goto)
            
            elif acao == 'acc':
                self.gerador.gerar('PARA')
                
                self.tabela.imprimir()
                self.gerador.imprimir()
                
                if self.erros_semanticos:
                    print("\nerros semanticos encontrados")
                    for erro in self.erros_semanticos:
                        print(f"{erro}")
                    print("\nanalise sintatica funcionou | analise semantica falhou")
                    return False
                
                print("\nanalise sintatica funcionou | analise semantica funcionou")
                return True
    
    def erro_sintatico(self, estado, token, valor):
        print(f"\n[ERRO SINTATICO] Linha {self.linha_atual}")
        print(f"  Estado: {estado}")
        print(f"  Token Encontrado: '{token}' (Valor: {valor})")