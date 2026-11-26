# Digital Ops Monitor — Sustentação de Plataformas Digitais & BI

Projeto desenvolvido para simular a rotina de **sustentação, monitoramento de integrações e análise de incidentes** de um Escritório Digital, cobrindo desde a coleta e modelagem dimensional de logs até a visualização executiva em BI e documentação operacional (*Runbook*).

## Arquitetura da Solução

```text
[Sistemas Origem: SAP, SharePoint, DW]
               │
               ▼  (Simulação de Execuções & Logs via Python)
[Banco Relacional SQLite — Star Schema]
               │
               ▼  (Camada Analítica via SQL View)
[Dashboard Executivo — Power BI Desktop]
               │
               ▼  (Atendimento & Resolução)
[Manual de Troubleshooting (docs/troubleshooting.md)]