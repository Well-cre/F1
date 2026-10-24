# Pipeline de carga

O pipeline principal coleta dados relevantes para uma etapa e sessão específicos.

## Execução

```bash
poetry run python scripts/fetch_session.py --meeting-key 1234 --session-key 5678
```

## Recursos consultados

- `sessions`
- `drivers`
- `laps`
- `session_result`

## Fluxo

1. Definir os filtros por etapa e sessão.
2. Consultar os endpoints principais.
3. Normalizar registros.
4. Persistir em `data/`.
5. Reexecutar sem duplicação.

## Idempotência

A rotina de escrita compara a representação JSON dos registros e ignora duplicatas antes de gravar no arquivo final.
