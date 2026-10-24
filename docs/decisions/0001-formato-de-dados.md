# 0001 — Formato de persistência dos dados

## Status

Aceito

## Contexto

O projeto exige baixa complexidade inicial, reprocessamento idempotente e compatibilidade com testes automatizados sem depender de infraestrutura externa.

## Decisão

Persistir os registros em arquivos JSON locais dentro do diretório `data/`.

## Consequências

### Positivas

- Simplicidade de uso e depuração
- Reprocessamento simples
- Compatibilidade com CI e execução local
- Fácil inspeção humana dos dados

### Negativas

- Não é um armazenamento transacional para grande volume
- Não é ideal para consultas analíticas complexas

## Observação final

Essa decisão atende ao MVP e reduz acoplamento com infraestrutura antes da maturidade do projeto.
