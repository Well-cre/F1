# Plano de criação do projeto F1

## 1. Objetivo

Construir um projeto Python de engenharia de dados para extrair, validar,
transformar e disponibilizar dados históricos de Fórmula 1 da API OpenF1. O
projeto deve ser modular, reproduzível, testável e documentado, seguindo os
padrões definidos em [`skill.md`](./skill.md).

O MVP utilizará os dados históricos gratuitos da API, disponíveis a partir de
2023. A coleta de dados em tempo real não faz parte do escopo inicial, pois
requer assinatura paga. A API será consumida por requisições HTTP GET à base
`https://api.openf1.org/v1/`, utilizando JSON como formato padrão.

## 2. Escopo do MVP

### Incluído

- Consultar etapas, sessões e pilotos para identificar os dados disponíveis.
- Coletar dados de voltas e resultados de sessões, filtrando as consultas por
  identificadores como `meeting_key`, `session_key` e `driver_number`.
- Validar e normalizar os registros antes de disponibilizá-los.
- Permitir reprocessamento idempotente para evitar duplicação de dados.
- Registrar início, conclusão, contagens e falhas das execuções.
- Disponibilizar testes automatizados sem depender de chamadas reais à API.
- Documentar instalação, uso, arquitetura e operação.

### Fora do escopo inicial

- Dados de telemetria e localização em alto volume (`car_data` e `location`).
- Consumo de dados em tempo real, que exige assinatura.
- Rádio de equipe, dashboards e interfaces visuais.
- Orquestração distribuída ou infraestrutura de nuvem antes de existir uma
  necessidade concreta.

Endpoints adicionais, como `weather`, `race_control`, `pit`, `stints`,
`position` e campeonatos, poderão ser incorporados após a validação do fluxo
principal. Os endpoints de campeonato são beta, e os dados de rádio são
parciais.

## 3. Arquitetura proposta

O fluxo deverá separar as responsabilidades em etapas independentes:

1. **Extração:** cliente HTTP para a OpenF1, com parâmetros de consulta,
   timeout e tratamento explícito de respostas inválidas ou falhas externas.
2. **Validação e transformação:** validação dos campos recebidos e normalização
   dos registros em estruturas tipadas; manter regras de negócio independentes
   do cliente HTTP e do destino dos dados.
3. **Persistência ou disponibilização:** gravar ou expor os dados no formato e
   destino definidos para o projeto. Essa escolha deve ser confirmada antes de
   implementar a carga, pois os documentos de referência não especificam o
   destino.
4. **Orquestração:** coordenar a execução das etapas, permitir filtros por
   temporada/etapa/sessão e produzir logs úteis para acompanhar a execução.

As dependências externas deverão ser isoladas para que testes unitários possam
substituir a API e o destino por implementações controladas. A configuração
específica do ambiente deverá vir de variáveis de ambiente ou mecanismo seguro,
sem credenciais ou segredos versionados.

## 4. Fases de implementação

### Fase 1 — Fundação do projeto

- Completar a estrutura `src` existente, mantendo o pacote `f1`.
- Configurar Poetry em `pyproject.toml`, declarar dependências de produção e
  desenvolvimento e versionar `poetry.lock`.
- Adicionar configurações do Ruff, pytest, cobertura e MkDocs Material.
- Criar os diretórios de documentação, scripts e testes previstos no padrão.

**Saída:** pacote instalável e ambiente de desenvolvimento reproduzível.

### Fase 2 — Contrato e cliente OpenF1

- Definir os endpoints do MVP e os parâmetros suportados para cada consulta.
- Implementar um cliente HTTP reutilizável, sem misturar chamadas externas com
  regras de transformação.
- Validar respostas e propagar erros com contexto suficiente para diagnóstico.
- Confirmar o comportamento de timeout, respostas vazias e indisponibilidade
  da API, sem presumir limites ou garantias que não estejam documentados.

**Saída:** acesso controlado e testável aos dados de reuniões, sessões, pilotos,
voltas e resultados.

### Fase 3 — Transformação e fluxo de dados

- Definir modelos tipados para os dados relevantes ao MVP.
- Normalizar datas e horários em UTC e validar identificadores e campos
  necessários.
- Separar extração, transformação e carga em componentes pequenos e coesos.
- Decidir o destino dos dados antes da implementação da persistência; registrar
  a escolha e suas implicações na documentação de arquitetura.
- Projetar a carga para ser idempotente e possibilitar reprocessamento quando
  a origem e o destino permitirem.

**Saída:** fluxo de dados executável de ponta a ponta, com destino definido.

### Fase 4 — Testes e confiabilidade

- Criar testes unitários para transformações, validações e casos de borda.
- Criar testes do cliente e do fluxo usando respostas simuladas, sem chamadas
  reais durante a suíte unitária.
- Cobrir respostas vazias, dados inválidos e falhas externas.
- Atingir ao menos 50% de cobertura global e buscar mais de 80% nos módulos de
  negócio e transformação.
- Verificar reprocessamento para prevenir duplicações.

**Saída:** comportamento validado automaticamente e falhas previsíveis.

### Fase 5 — Documentação, CI e entrega

- Atualizar o README com propósito, pré-requisitos, instalação e comandos
  principais.
- Documentar arquitetura, endpoints utilizados, componentes, execução,
  reprocessamento e troubleshooting em `docs/`.
- Configurar CI para instalar via Poetry e executar Ruff, formatação, pytest,
  validação de cobertura e build do MkDocs.
- Revisar o PR, incluindo mudanças, testes executados e impactos operacionais.

**Saída:** projeto documentado, validado pela CI e pronto para evolução.

## 5. Estrutura alvo

```text
F1/
├── src/
│   └── f1/
│       ├── __init__.py
│       ├── config.py
│       ├── clients/
│       ├── pipelines/
│       ├── services/
│       └── ...
├── tests/
├── docs/
│   ├── index.md
│   ├── architecture.md
│   ├── pipelines/
│   └── operations/
├── scripts/
├── pyproject.toml
├── poetry.lock
├── mkdocs.yml
└── README.md
```

Os nomes e módulos definitivos devem acompanhar as responsabilidades que
emergirem durante a implementação; não criar camadas sem necessidade.

## 6. Critérios de conclusão

- Código produtivo fica em `src/f1/`; utilitários em `scripts/`; testes em
  `tests/`.
- Dependências são gerenciadas pelo Poetry e o lock file é versionado.
- Funções públicas novas possuem type hints e responsabilidades claras.
- Logs usam o módulo `logging` e não expõem segredos ou dados sensíveis.
- Testes automatizados passam, incluindo a cobertura global mínima de 50%.
- Ruff check e Ruff format check passam.
- A documentação MkDocs compila e reflete o comportamento implementado.
- A CI executa todas as verificações obrigatórias e não aprova alterações com
  etapas falhas.

## 7. Referências e decisões pendentes

- [`doc_api.md`](./doc_api.md): resumo dos endpoints, filtros, formatos e
  limitações da OpenF1.
- [`skill.md`](./skill.md): padrões de estrutura, dependências, tipagem, testes,
  documentação, observabilidade, CI e entrega.
- **Decisão pendente antes da Fase 3:** definir o formato e o destino de
  persistência dos dados, conforme o uso esperado pelo projeto.
