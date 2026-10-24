# Projeto F1

Este projeto implementa um pipeline de dados para consultar a API pública OpenF1, validar e normalizar registros de sessões de Fórmula 1 e gravá-los em arquivos JSON locais para uso posterior e reprocessamento seguro.

## Visão geral

- Extração de dados de sessões, pilotos, voltas e resultados
- Validação dos campos críticos antes da persistência
- Normalização de datas e identificadores
- Persistência idempotente em disco local
- Testes automatizados sem depender da API real

## Fluxo principal

1. O cliente HTTP consulta os endpoints da OpenF1.
2. O pipeline normaliza os registros recebidos.
3. O destino JSON salva os dados em `data/`.
4. A execução pode ser repetida sem duplicar registros.

## Endpoints principais

- `sessions`
- `drivers`
- `laps`
- `session_result`

## Observabilidade

Os logs de execução usam o módulo `logging` para registrar início, filtros, contagem de registros e falhas.

## Comandos e dashboard

Liste as sessões disponíveis na OpenF1 e use os identificadores retornados para
executar a coleta:

```bash
poetry run python scripts/list_sessions.py
poetry run python scripts/fetch_session.py --meeting-key <meeting_key> --session-key <session_key>
```

Os arquivos `sessions.json`, `drivers.json`, `laps.json` e `session_result.json`
são gravados em `data/` por padrão. Para visualizá-los no dashboard:

```bash
poetry run streamlit run src/f1/dashboard.py
```

O diretório de saída pode ser configurado com a variável `F1_OUTPUT_DIR`.
