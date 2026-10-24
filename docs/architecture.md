# Arquitetura

A arquitetura foi organizada em camadas para manter responsabilidades separadas e permitir testes focados.

## Camadas

### Cliente HTTP

O módulo `src/f1/clients/openf1.py` encapsula chamadas à API pública e trata códigos HTTP diferentes de 200.

### Normalização e validação

O módulo `src/f1/transforms.py` converte datas para UTC e padroniza campos numéricos e textuais.

### Persistência

O módulo `src/f1/storage.py` grava registros em JSON em `data/`. A escrita é idempotente: múltiplas execuções com os mesmos dados não geram duplicações.

### Pipeline

O módulo `src/f1/pipelines/session_pipeline.py` orquestra a extração de múltiplos recursos e coordena a escrita em disco.

## Decisão de destino

Foi escolhido o armazenamento em JSON local em vez de banco de dados para reduzir complexidade inicial e manter o projeto reproduzível em ambiente local e em CI. O formato está documentado em `docs/decisions/0001-formato-de-dados.md`.
