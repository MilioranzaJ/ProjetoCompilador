import os

MAPA_NOMES = {
    "$ident": "VAR", "ident": "IDENT", "numero_real": "NUMERO_REAL",
    "floatval(readline());": "FLOATVAL", "EOF": "$",
    "<?php": "PHP_OPEN", "?>": "PHP_CLOSE",
    
    "num": "NUMERO_REAL", "real": "NUMERO_REAL", "digito": "NUMERO_REAL",
    "numero": "NUMERO_REAL", "NUMBER": "NUMERO_REAL",
    ";": "PV", "=": "ATRIB", ",": "VIRG", ".": "PONTO",
    "(": "ABRE_P", ")": "FECHA_P", "{": "ABRE_C", "}": "FECHA_C",
    "+": "SOMA", "-": "SUB", "*": "MULT", "/": "DIV",
    ">": "MAIOR", "<": "MENOR", ">=": "MAIOR_IGUAL", "<=": "MENOR_IGUAL",
    "==": "IGUAL", "!=": "DIFERENTE"
}

FOLLOW = {
    "<programa>": ["$"], "<corpo>": ["PHP_CLOSE"],
    "<dc>": ["VAR", "ECHO", "IF", "WHILE"],
    "<dc_v>": ["VAR", "FUNCTION", "ECHO", "IF", "WHILE"],
    "<dc_f>": ["VAR", "ECHO", "IF", "WHILE"],
    "<comandos>": ["PHP_CLOSE", "FECHA_C"],
    "<comando>": ["VAR", "ECHO", "IF", "WHILE", "PHP_CLOSE", "FECHA_C"],
    "<mais_dc>": ["VAR", "ECHO", "IF", "WHILE"],
    "<atribuicao_opcional>": ["VAR", "FUNCTION", "ECHO", "IF", "WHILE"],
    "<expressao>": ["PV", "VIRG", "DIFERENTE", "MENOR", "MENOR_IGUAL", "IGUAL", "MAIOR", "MAIOR_IGUAL", "FECHA_P"],
    "<termo>": ["SOMA", "SUB", "PV", "VIRG", "DIFERENTE", "MENOR", "MENOR_IGUAL", "IGUAL", "MAIOR", "MAIOR_IGUAL", "FECHA_P"],
    "<op_un>": ["VAR", "ABRE_P", "NUMERO_REAL"],
    "<parametros>": ["ABRE_C"], "<lista_par>": ["FECHA_P"], "<mais_par>": ["FECHA_P"],
    "<corpo_f>": ["FECHA_C"], "<dc_loc>": ["VAR", "ECHO", "IF", "WHILE"],
    "<mais_dcloc>": ["VAR", "ECHO", "IF", "WHILE"], "<lista_arg>": ["PV"],
    "<argumentos>": ["FECHA_P"], "<mais_ident>": ["FECHA_P"],
    "<mais_comandos>": ["PHP_CLOSE", "FECHA_C"], "<restoIdent>": ["PV"],
    "<condicao>": ["FECHA_P"],
    "<relacao>": ["VAR", "ABRE_P", "SUB", "FLOATVAL", "NUMERO_REAL"],
    "<outros_termos>": ["PV", "VIRG", "DIFERENTE", "MENOR", "MENOR_IGUAL", "IGUAL", "MAIOR", "MAIOR_IGUAL", "FECHA_P"],
    "<op_ad>": ["VAR", "ABRE_P", "SUB", "NUMERO_REAL"],
    "<fator>": ["MULT", "DIV", "SOMA", "SUB", "PV", "VIRG", "DIFERENTE", "MENOR", "MENOR_IGUAL", "IGUAL", "MAIOR", "MAIOR_IGUAL", "FECHA_P"],
    "<mais_fatores>": ["SOMA", "SUB", "PV", "VIRG", "DIFERENTE", "MENOR", "MENOR_IGUAL", "IGUAL", "MAIOR", "MAIOR_IGUAL", "FECHA_P"],
    "<op_mul>": ["VAR", "ABRE_P", "NUMERO_REAL"],
    "<pfalsa>": ["VAR", "ECHO", "IF", "WHILE", "PHP_CLOSE", "FECHA_C"]
}

REGRAS_NUMERADAS = [
    ("S'", 1), ("<programa>", 3), ("<corpo>", 2), ("<dc>", 2), ("<dc>", 1), ("<dc>", 0),
    ("<mais_dc>", 1), ("<mais_dc>", 0), ("<dc_v>", 2), ("<atribuicao_opcional>", 3),
    ("<atribuicao_opcional>", 1), ("<dc_f>", 6), ("<parametros>", 3), ("<parametros>", 2),
    ("<lista_par>", 2), ("<mais_par>", 3), ("<mais_par>", 0), ("<corpo_f>", 2),
    ("<dc_loc>", 2), ("<dc_loc>", 0), ("<mais_dcloc>", 1), ("<mais_dcloc>", 0),
    ("<comandos>", 2), ("<mais_comandos>", 1), ("<mais_comandos>", 0), ("<comando>", 5),
    ("<comando>", 8), ("<comando>", 7), ("<comando>", 3), ("<restoIdent>", 2),
    ("<restoIdent>", 1), ("<pfalsa>", 4), ("<pfalsa>", 0), ("<condicao>", 3),
    ("<relacao>", 1), ("<relacao>", 1), ("<relacao>", 1), ("<relacao>", 1),
    ("<relacao>", 1), ("<relacao>", 1), ("<expressao>", 6), ("<expressao>", 2),
    ("<outros_termos>", 3), ("<outros_termos>", 0), ("<op_ad>", 1), ("<op_ad>", 1),
    ("<termo>", 3), ("<op_un>", 1), ("<op_un>", 0), ("<mais_fatores>", 3),
    ("<mais_fatores>", 0), ("<op_mul>", 1), ("<op_mul>", 1), ("<fator>", 1),
    ("<fator>", 1), ("<fator>", 3), ("<lista_arg>", 3), ("<lista_arg>", 2),
    ("<argumentos>", 2), ("<mais_ident>", 3), ("<mais_ident>", 0),
    ("<expressao>", 1),   
    ("<comando>", 3),     
]

ARQUIVO_ENTRADA = "arquivo.txt"

def ler_lista_na_mao(texto_lista):
    itens = []
    atual = ""
    dentro_aspas = False
    tipo_aspas = '' 

    texto_limpo = texto_lista.strip()
    if texto_limpo.startswith('['): texto_limpo = texto_limpo[1:]
    if texto_limpo.endswith(']'): texto_limpo = texto_limpo[:-1]
    
    for char in texto_limpo:
        if char in ["'", '"']:
            if not dentro_aspas:
                dentro_aspas = True
                tipo_aspas = char
            elif char == tipo_aspas:
                dentro_aspas = False 
            atual += char
        elif char == ',':
            if dentro_aspas:
                atual += char 
            else:
                itens.append(atual.strip())
                atual = "" 
        else:
            atual += char
    if atual: itens.append(atual.strip())
    
    lista_final = []
    for item in itens:
        if (item.startswith("'") and item.endswith("'")) or (item.startswith('"') and item.endswith('"')):
            lista_final.append(item[1:-1])
        else:
            lista_final.append(item)
    return lista_final

def limpar_simbolo(simb):
    s = simb.replace('°', '').strip()
    return MAPA_NOMES.get(s, s.upper())

def encontrar_numero_regra(lhs, rhs_str):
    rhs_limpo = rhs_str.replace('°', '').strip().split()
    tam = len(rhs_limpo)
    
    if tam == 1 and (rhs_limpo[0] == 'Î»' or rhs_limpo[0] == 'î»'): 
        tam = 0
        
    for i, (rl, rt) in enumerate(REGRAS_NUMERADAS):
        if rl == lhs and rt == tam: return i
    return 0

def escrever_csv_manual(caminho, dados_dict, colunas):
    with open(caminho, "w", encoding="utf-8") as f:
        linha_cabecalho = '"ESTADO";' + ';'.join([f'"{c}"' for c in colunas])
        f.write(linha_cabecalho + "\n")
        
        todos_estados = sorted(dados_dict.keys())
        if not todos_estados: return
        
        ultimo = max(todos_estados)
        for est in range(ultimo + 1):
            linha = [f'"{est}"']
            for col in colunas:
                valor = dados_dict.get(est, {}).get(col, "")
                if valor: linha.append(f'"{valor}"')
                else: linha.append('""')
            f.write(";".join(linha) + "\n")

def main():
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"ERRO: '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    tabela_action = {}
    tabela_goto = {}
    
    try:
        with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except:
        with open(ARQUIVO_ENTRADA, "r", encoding="latin-1") as f:
            linhas = f.readlines()

    for linha in linhas:
        if "=>" not in linha: continue
        
        try:
            partes = linha.split("=>")
            estado_atual = int(partes[0].strip())
            conteudo_bruto = partes[1].strip()
            
            dados = ler_lista_na_mao(conteudo_bruto)
            
            lhs = dados[0]
            rhs_com_ponto = dados[1]
            proximo_estado = int(dados[2])
            
            partes_rhs = rhs_com_ponto.split()
            
            eh_reduce = False
            
            if rhs_com_ponto.endswith('°'):
                eh_reduce = True
            elif '°Î»' in rhs_com_ponto or '° Î»' in rhs_com_ponto or '°î»' in rhs_com_ponto:
                eh_reduce = True

            if eh_reduce:
                if lhs == "<S'>" and "<programa>°" in rhs_com_ponto:
                    tabela_action.setdefault(estado_atual, {})['$'] = 'acc'
                    continue
                
                num_regra = encontrar_numero_regra(lhs, rhs_com_ponto)
                
                for item in FOLLOW.get(lhs, []):
                    tok = limpar_simbolo(item)
                    tabela_action.setdefault(estado_atual, {})[tok] = f"r{num_regra}"
            
            else:
                idx = -1
                for i, p in enumerate(partes_rhs):
                    if '°' in p: idx = i; break
                
                simb = partes_rhs[idx].replace('°', '')
                if not simb and idx+1 < len(partes_rhs): simb = partes_rhs[idx+1]
                
                token = limpar_simbolo(simb)
                
                if token.startswith('<'):
                    tabela_goto.setdefault(estado_atual, {})[token] = proximo_estado
                else:
                    tabela_action.setdefault(estado_atual, {})[token] = f"s{proximo_estado}"
                    
        except Exception:
            continue

    os.makedirs("saida", exist_ok=True)
    
    cols_action = sorted(list(set(k for r in tabela_action.values() for k in r)))
    escrever_csv_manual("saida/action.csv", tabela_action, cols_action)
    
    cols_goto = sorted(list(set(k for r in tabela_goto.values() for k in r)))
    escrever_csv_manual("saida/goto.csv", tabela_goto, cols_goto)
    
    with open("saida/tabelas.py", "w", encoding="utf-8") as f:
        f.write("# tabelas.py\nTABELA_ACTION = {\n")
        for e in sorted(tabela_action.keys()):
            for k,v in tabela_action[e].items():
                f.write(f"    ({e}, '{k}'): '{v}',\n")
        f.write("}\nTABELA_GOTO = {\n")
        for e in sorted(tabela_goto.keys()):
            for k,v in tabela_goto[e].items():
                nt = k.replace('<','').replace('>','')
                f.write(f"    ({e}, '{nt}'): {v},\n")
        f.write("}\nREGRAS_GRAMATICA = {\n")
        for i, (l, q) in enumerate(REGRAS_NUMERADAS):
            l_limpo = l.replace('<','').replace('>','')
            f.write(f"    'r{i}': (\"{l_limpo}\", {q}),\n")
        f.write("}\n")
        
if __name__ == "__main__":
    main()