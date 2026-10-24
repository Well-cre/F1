# Validação de dados

A validação foi implementada em etapas simples e explícitas para manter regras de negócio separadas da infraestrutura.

## Regras principais

- Campos `meeting_key` e `session_key` devem ser convertidos para inteiros quando disponíveis.
- Datas devem ser normalizadas para UTC em ISO 8601.
- Registros vazios ou nulos devem ser ignorados de forma segura.
- Respostas da API fora do formato esperado são rejeitadas com erro explícito.

## Exemplo

```python
from f1.transforms import normalize_record

record = {"meeting_key": "123", "session_start": "2024-08-02T12:34:56+02:00"}
print(normalize_record(record))
```

Saída esperada:

```python
{"meeting_key": 123, "session_start": "2024-08-02T10:34:56+00:00"}
```
