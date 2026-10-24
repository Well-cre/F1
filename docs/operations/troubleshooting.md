# Troubleshooting

## Problemas comuns

### 1. Falha na consulta HTTP

Verifique se a URL base da OpenF1 está correta e se a API está acessível. O cliente lança erro explícito para status HTTP diferente de `200`.

### 2. Dados incompletos

Se a resposta vier vazia, o pipeline registra a consulta e salva uma estrutura vazia em disco. Isso é útil para diagnosticar falhas em filtros.

### 3. Reprocessamento duplicado

A persistência em JSON usa deduplicação por representação serializada. Isso reduz riscos de duplicação em execuções repetidas do mesmo conjunto de dados.

## Logs úteis

- Início de consulta por recurso
- Número de registros recebidos
- Número de registros gravados
- Exceções com contexto operacional
