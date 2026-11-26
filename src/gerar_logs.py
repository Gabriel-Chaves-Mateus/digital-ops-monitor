import sqlite3
import random
from datetime import datetime, timedelta
import os
import csv

# Caminhos dos arquivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sustentacao.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
CSV_EXPORT_PATH = os.path.join(BASE_DIR, "database", "dados_powerbi.csv")

def inicializar_banco():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn

def popular_dimensoes(conn):
    cursor = conn.cursor()
    
    sistemas = [
        (1, "SAP S/4HANA", "ERP / Produção", "Alta"),
        (2, "SharePoint Online", "Colaboração M365", "Media"),
        (3, "Data Warehouse Corporativo", "Dados & Analytics", "Alta"),
        (4, "Portal Power Automate", "Automação de Processos", "Media")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dim_sistema VALUES (?, ?, ?, ?)", sistemas)

    rotinas = [
        (101, "Carga_Producao_Fabrica_01", "ETL", "Diaria", 1),
        (102, "Atualizacao_Painel_OEE", "Dashboard BI", "Diaria", 3),
        (103, "Sync_Solicitacoes_Acesso", "Automacao RPA", "Horaria", 2),
        (104, "Extracao_Estoque_Materiais", "ETL", "Diaria", 1),
        (105, "Relatorio_SLA_Chamados", "Dashboard BI", "Diaria", 3),
        (106, "Fluxo_Aprovacao_Compras", "Automacao RPA", "Diaria", 4)
    ]
    cursor.executemany("INSERT OR IGNORE INTO dim_rotina VALUES (?, ?, ?, ?, ?)", rotinas)
    conn.commit()

def gerar_historico_execucoes(conn, dias=30):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fato_execucoes") # Limpa para gerar novo cenário
    
    erros_possiveis = [
        ("ERR_SAP_504", "Timeout na extracao RFC do SAP"),
        ("ERR_SQL_LOCK", "Deadlock na tabela de destino DW"),
        ("ERR_AUTH_401", "Token de autenticacao SharePoint expirado"),
        ("ERR_DATA_NULL", "Coluna obrigatoria veio nula na origem")
    ]

    hoje = datetime.now()
    registros = []

    for dia_offset in range(dias, -1, -1):
        data_base = hoje - timedelta(days=dia_offset)
        
        for id_rotina in range(101, 107):
            # Simula execucao matinal
            hora_exec = data_base.replace(hour=random.randint(5, 8), minute=random.randint(0, 59), second=0)
            
            # 85% de chance de sucesso, 10% de falha, 5% de alerta (lentidao)
            sorteio = random.random()
            if sorteio < 0.85:
                status = "Sucesso"
                duracao = random.randint(30, 180)
                cod_erro, msg_erro = None, None
            elif sorteio < 0.95:
                status = "Falha"
                duracao = random.randint(10, 60)
                cod_erro, msg_erro = random.choice(erros_possiveis)
            else:
                status = "Alerta"
                duracao = random.randint(300, 600) # Demorou muito mais que o normal
                cod_erro, msg_erro = "WARN_PERF", "Tempo de execucao acima do limite esperado"

            registros.append((
                id_rotina,
                hora_exec.strftime("%Y-%m-%d %H:%M:%S"),
                status,
                duracao,
                cod_erro,
                msg_erro
            ))

    cursor.executemany("""
        INSERT INTO fato_execucoes (id_rotina, data_execucao, status, duracao_segundos, codigo_erro, mensagem_erro)
        VALUES (?, ?, ?, ?, ?, ?)
    """, registros)
    conn.commit()
    print(f"[OK] {len(registros)} execucoes simuladas com sucesso!")

def exportar_para_bi(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vw_monitoramento_sustentacao")
    colunas = [desc[0] for desc in cursor.description]
    linhas = cursor.fetchall()

    with open(CSV_EXPORT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(colunas)
        writer.writerows(linhas)
    print(f"[OK] Base exportada para BI em: {CSV_EXPORT_PATH}")

if __name__ == "__main__":
    conexao = inicializar_banco()
    popular_dimensoes(conexao)
    gerar_historico_execucoes(conexao, dias=30)
    exportar_para_bi(conexao)
    conexao.close()