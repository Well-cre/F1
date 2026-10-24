# Python Engineering Standards

## 1. Visão Geral

Este padrão define requisitos mínimos para desenvolver, testar, documentar e entregar projetos Python de Engenharia de Dados. Aplica-se a engenheiros de dados, analistas de dados com perfil de engenharia e desenvolvedores Python.

Os padrões têm como objetivos:

- **Manutenibilidade:** tornar alterações e correções seguras e previsíveis.
- **Escalabilidade:** permitir que pipelines e componentes evoluam com o volume de dados e as necessidades do negócio.
- **Observabilidade:** facilitar o acompanhamento de execuções, falhas e qualidade dos dados.
- **Testabilidade:** detectar regressões antes que cheguem aos ambientes compartilhados ou produtivos.
- **Reutilização:** reduzir duplicação e incentivar componentes com responsabilidades bem definidas.
- **Segurança:** proteger credenciais, dados e infraestrutura.
- **Padronização entre equipes:** tornar projetos consistentes, revisáveis e fáceis de integrar.

Os termos normativos são usados com o seguinte significado:

- **MUST:** requisito obrigatório.
- **MUST NOT:** prática proibida.
- **SHOULD:** recomendação que deve ser seguida, salvo justificativa técnica registrada.
- **MAY:** prática opcional, aplicável quando trouxer benefício claro.

## 2. Estrutura de Projeto

Todo projeto Python **MUST** adotar `src layout` e a estrutura abaixo. `projeto` representa o nome do pacote Python, em letras minúsculas e com `_` quando necessário.

```text
projeto/
├── src/
│   └── projeto/
│       ├── __init__.py
│       ├── config.py
│       ├── pipelines/
│       ├── services/
│       └── ...
├── tests/
├── docs/
│   └── index.md
├── scripts/
├── pyproject.toml
├── poetry.lock
├── mkdocs.yml
└── README.md
```

Responsabilidades:

- `src/projeto/`: pacote importável e todo o código de negócio e de produção.
- `tests/`: testes automatizados, organizados de forma correspondente aos módulos de `src/projeto/`.
- `docs/`: documentação técnica e operacional, incluindo arquitetura, componentes e pipelines.
- `scripts/`: utilitários de desenvolvimento, manutenção e operação que não fazem parte do pacote produtivo.
- `pyproject.toml`: metadados do projeto, dependências e configurações das ferramentas.
- `poetry.lock`: versões resolvidas das dependências, versionadas para instalações reproduzíveis.
- `mkdocs.yml`: configuração do site de documentação MkDocs.
- `README.md`: apresentação do projeto, pré-requisitos, instalação e comandos de uso mais comuns.

Regras mandatórias:

- Todo código de negócio **MUST** ficar dentro de `src/projeto/`.
- Código produtivo fora da estrutura `src` **MUST NOT** ser criado.
- Scripts utilitários **MUST** ficar em `scripts/`; **MUST NOT** ser usados para contornar a organização do pacote.
- Testes automatizados **MUST** ficar em `tests/`.
- O pacote **MUST** ser instalável a partir do `src layout` por meio da configuração do Poetry.

## 3. Gerenciamento de Dependências

Poetry é o gerenciador obrigatório de dependências e ambientes virtuais. `pyproject.toml` é a fonte única de definição de dependências; `poetry.lock` registra as versões resolvidas e **MUST** ser versionado.

### MUST

- Utilizar Poetry para gerenciar dependências e ambientes virtuais.
- Declarar dependências de produção e desenvolvimento em `pyproject.toml`.
- Versionar `poetry.lock` junto com o projeto.
- Utilizar `poetry install` para instalar as dependências declaradas.

### MUST NOT

- Executar `pip install` para instalar dependências.
- Manter manualmente um `requirements.txt` como fonte paralela de dependências.
- Instalar dependências fora do ambiente gerenciado pelo Poetry.

Exemplos:

```bash
poetry install
poetry add pandas
poetry add --group dev pytest
poetry remove pandas
poetry update
poetry run task test
poetry run task lint
poetry run task format
poetry run task docs
poetry run pytest
poetry run python scripts/reprocessar_lote.py
```

`poetry update` **SHOULD** ser usado de forma deliberada, revisando as alterações do lock file e executando os testes antes de integrá-las.

Os atalhos `task test`, `task lint`, `task format` e `task docs` **MUST** ser definidos em `[tool.taskipy.tasks]` no `pyproject.toml`, usando Taskipy como dependência de desenvolvimento. Eles executam, respectivamente, os testes, o Ruff Check, a formatação com Ruff e o build do site MkDocs.

## 4. Organização do Código

O código **MUST** seguir estes princípios:

- **Single Responsibility Principle:** cada módulo, classe ou função deve ter uma responsabilidade principal.
- **Separation of Concerns:** separar regras de negócio, acesso a dados, configuração, orquestração e apresentação.
- **Clean Code:** priorizar nomes claros, fluxo simples e interfaces explícitas.
- **SOLID:** aplicar seus princípios quando forem adequados à complexidade e ao contexto.
- **DRY:** manter uma única implementação para uma regra de negócio compartilhada.
- **KISS:** escolher a solução mais simples que satisfaça os requisitos.

### MUST

- Criar módulos pequenos, coesos e com interfaces claras.
- Utilizar type hints em código novo.
- Isolar regras de negócio de infraestrutura, como banco de dados, armazenamento em nuvem e ferramentas de orquestração.
- Separar etapas de extração, transformação e carga quando isso tornar o fluxo mais claro e testável.
- Projetar operações de pipeline para serem idempotentes quando o processo e a origem dos dados permitirem.

### MUST NOT

- Criar funções ou módulos excessivamente grandes, com múltiplas responsabilidades.
- Misturar regras de negócio diretamente com detalhes de infraestrutura.
- Duplicar lógica de transformação ou validação.

Exemplo de separação:

```python
def normalizar_cliente(registro: dict[str, str]) -> dict[str, str]:
    return {
        "id": registro["id"].strip(),
        "nome": registro["nome"].strip().title(),
    }
```

A função acima implementa uma transformação independente. A leitura do arquivo de origem e a gravação no destino **SHOULD** ser tratadas em componentes separados.

## 5. Qualidade de Código

Ruff é a única ferramenta oficial para lint, formatação e ordenação de imports. A configuração **MUST** ficar em `pyproject.toml`, garantindo resultados consistentes entre desenvolvedores e CI.

### MUST

- Executar Ruff em alterações de código Python.
- Corrigir os problemas encontrados antes de abrir ou aprovar um PR.
- Aplicar a formatação oficial do Ruff.

Comandos:

```bash
poetry run ruff check .
poetry run ruff check . --fix
poetry run ruff format .
poetry run ruff format --check .
poetry run task lint
poetry run task format
```

Ruff automatiza a detecção de erros comuns, aplica convenções de estilo, organiza imports e reduz diferenças de formatação em revisões. Outras ferramentas de lint, formatação ou ordenação de imports **MUST NOT** ser adotadas como padrão concorrente do time.

## 6. Padrões de Tipagem

### MUST

- Declarar type hints em todos os parâmetros e retornos de funções públicas.
- Utilizar recursos de tipagem do módulo `typing` quando apropriados.
- Representar configurações e dados estruturados com `dataclasses` ou Pydantic quando isso melhorar validação e clareza.

### SHOULD

- Utilizar `Protocol` para definir contratos estruturais e facilitar substituições em testes.
- Preferir tipos específicos, como `Sequence[str]`, `Decimal` ou tipos de domínio, a `Any`.
- Utilizar tipos de domínio para valores com significado ou validações próprias, quando isso reduzir ambiguidades.

### MUST NOT

- Utilizar `Any` de forma excessiva ou para evitar definir contratos de tipos.

Exemplo:

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Venda:
    identificador: str
    data: date
    valor: Decimal
```

## 7. Testes Automatizados

`pytest` é o framework oficial de testes. O limite de cobertura é de **50% no mínimo** para o projeto; novos módulos e alterações **SHOULD** buscar cobertura superior a 80% para o código relevante, sem substituir testes de comportamento por uma métrica isolada.

### MUST

- Manter cobertura mínima global de 50%, validada automaticamente na CI.
- Criar um teste de regressão para cada bug corrigido.
- Criar testes para novas funcionalidades.
- Executar os testes antes de abrir um PR.

### SHOULD

- Buscar cobertura superior a 80% nos módulos de negócio e transformação.
- Utilizar testes parametrizados para validar múltiplos casos de entrada com a mesma regra.
- Testar casos de borda, dados inválidos e falhas de dependências externas.
- Preferir testes unitários rápidos e isolados; usar testes de integração para validar contratos entre componentes.

### MUST NOT

- Aprovar PR sem testes automatizados passando.
- Depender de serviços externos reais em testes unitários.

Estratégia **AAA** para organizar cada teste:

1. **Arrange:** preparar entradas, dependências e estado inicial.
2. **Act:** executar a ação testada.
3. **Assert:** verificar resultado e efeitos esperados.

Exemplo:

```python
import pytest


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [(" ana ", "Ana"), ("joao", "Joao")],
)
def test_normalizar_nome(entrada: str, esperado: str) -> None:
    # Arrange
    registro = {"id": "1", "nome": entrada}

    # Act
    resultado = normalizar_cliente(registro)

    # Assert
    assert resultado["nome"] == esperado
```

Comandos:

```bash
poetry run pytest
poetry run pytest --cov
poetry run pytest -vv
poetry run task test
```

## 8. Documentação

MkDocs Material é o padrão oficial para documentação técnica navegável. A documentação **MUST** ser mantida junto ao código no repositório.

### MUST

- Documentar a arquitetura e as decisões relevantes.
- Documentar componentes, suas responsabilidades e contratos.
- Documentar pipelines, etapas, entradas, saídas e estratégia de reprocessamento.
- Documentar dependências externas, permissões necessárias e modos de falha relevantes.
- Atualizar a documentação afetada na mesma alteração que muda o comportamento.

Estrutura recomendada:

```text
docs/
├── index.md
├── architecture.md
├── components/
│   └── validacao.md
├── pipelines/
│   └── carga_diaria.md
├── operations/
│   └── troubleshooting.md
└── decisions/
    └── 0001-formato-de-dados.md
```

`README.md` **SHOULD** apresentar o propósito do projeto, pré-requisitos, instalação com Poetry, comandos principais e links para a documentação completa. A documentação de um componente **SHOULD** estar próxima de seu código ou ser referenciada diretamente a partir dele.

Comandos:

```bash
poetry run mkdocs serve
poetry run mkdocs build
poetry run task docs
```

## 9. Logging e Observabilidade

O módulo padrão `logging` **MUST** ser utilizado em código produtivo. Registros devem fornecer contexto suficiente para investigar execuções e falhas de processamento, sem expor dados sensíveis.

### MUST

- Registrar erros relevantes com contexto operacional, como nome da etapa e identificador de execução quando disponível.
- Selecionar o nível de log de acordo com a gravidade e o impacto.
- Incluir informações que permitam correlacionar eventos da mesma execução, sem registrar segredos ou conteúdo sensível.

### MUST NOT

- Utilizar `print` para logging em código produtivo.
- Registrar credenciais, tokens ou dados pessoais desnecessários.

Níveis:

- **INFO:** eventos normais relevantes, como início e conclusão de uma carga, incluindo contagens úteis.
- **WARNING:** condição inesperada ou degradação que permite continuar, mas requer atenção.
- **ERROR:** falha que impediu uma operação ou etapa; registrar contexto e, quando adequado, a exceção.
- **CRITICAL:** falha grave que compromete a execução ou o serviço e requer ação imediata.

Exemplo:

```python
import logging

logger = logging.getLogger(__name__)


def processar_lote(lote_id: str) -> None:
    logger.info("Iniciando processamento do lote %s", lote_id)
    try:
        ...
    except OSError:
        logger.exception("Falha ao acessar os dados do lote %s", lote_id)
        raise
```

## 10. Configuração e Segredos

### MUST

- Obter configurações específicas do ambiente por variáveis de ambiente ou por um mecanismo de configuração seguro que as utilize.
- Manter segredos fora do código-fonte e do controle de versão.
- Validar configurações obrigatórias no início da execução e falhar com mensagem clara quando estiverem ausentes ou inválidas.

### MUST NOT

- Incluir credenciais, tokens ou chaves diretamente no código.
- Versionar segredos ou arquivos locais que os contenham.

Exemplo:

```python
import os


def obter_bucket() -> str:
    bucket = os.environ.get("DATA_BUCKET")
    if not bucket:
        raise RuntimeError("A variável de ambiente DATA_BUCKET é obrigatória")
    return bucket
```

## 11. Integração Contínua

Todo projeto **MUST** executar, no mínimo, as etapas abaixo em sua pipeline de CI:

1. Instalação reproduzível via Poetry (`poetry install`).
2. Ruff Check (`poetry run ruff check .`).
3. Ruff Format Check (`poetry run ruff format --check .`).
4. Testes com pytest.
5. Validação de cobertura mínima de 50%.
6. Build da documentação (`poetry run mkdocs build`).

PR **MUST NOT** ser aprovado ou integrado se qualquer etapa obrigatória falhar. A CI **SHOULD** utilizar a versão de Python suportada pelo projeto e instalar dependências a partir do lock file.

## 12. Git e Pull Requests

### MUST

- Criar branches pequenas e focadas em uma alteração coerente.
- Manter PRs pequenos, com descrição do contexto, da solução e da validação executada.
- Exigir revisão de pelo menos uma pessoa antes da integração.
- Vincular mudanças a testes e documentação correspondentes.

Convenções sugeridas para branches:

```text
feature/adicionar-validacao
bugfix/corrigir-data-nula
hotfix/recuperar-carga
refactor/separar-leitura-e-transformacao
```

Commits **SHOULD** ser claros e descrever a alteração. PRs **SHOULD** informar impactos em dados, compatibilidade, configuração e operação, quando aplicável.

## 13. Definition of Done

Uma entrega só é considerada concluída quando todos os itens abaixo forem atendidos:

- Código implementado dentro da estrutura acordada.
- Ruff executado sem erros e formatação validada.
- Testes automatizados passando.
- Cobertura mínima de 50% atingida.
- Documentação atualizada quando aplicável.
- Revisão obrigatória realizada.
- Todas as etapas obrigatórias da CI aprovadas.

## 14. Exemplo de pyproject.toml

O exemplo abaixo usa a configuração moderna de projeto Poetry. Versões devem ser revisadas e atualizadas de forma controlada pelo time.

```toml
[project]
name = "projeto"
version = "0.1.0"
description = "Pipeline de Engenharia de Dados"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[tool.poetry]
packages = [{ include = "projeto", from = "src" }]

[tool.poetry.group.dev.dependencies]
ruff = "^0.11"
pytest = "^8.3"
pytest-cov = "^6.0"
mkdocs = "^1.6"
mkdocs-material = "^9.6"
taskipy = "^1.14"

[tool.taskipy.tasks]
test = "pytest"
lint = "ruff check ."
format = "ruff format ."
docs = "mkdocs build"

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=projeto --cov-report=term-missing --cov-fail-under=50"

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

O arquivo `mkdocs.yml` **MUST** declarar `material` como tema. Configuração mínima:

```yaml
site_name: Documentação do Projeto
theme:
  name: material
nav:
  - Início: index.md
  - Arquitetura: architecture.md
```

## 15. Checklist Final

Antes de abrir um Pull Request, confirme:

- [ ] O código de negócio está dentro de `src/projeto/`.
- [ ] Scripts utilitários estão em `scripts/` e testes em `tests/`.
- [ ] Dependências foram gerenciadas com Poetry e `poetry.lock` está atualizado e versionado.
- [ ] Nenhuma instalação foi feita com `pip install` e não há `requirements.txt` manual.
- [ ] Funções públicas possuem type hints e responsabilidades estão separadas.
- [ ] `poetry run ruff check .` passou.
- [ ] `poetry run ruff format --check .` passou.
- [ ] Novas funcionalidades e bugs corrigidos possuem testes.
- [ ] `poetry run pytest` passou e a cobertura mínima de 50% foi atingida.
- [ ] Logs usam `logging`, têm níveis apropriados e não expõem dados sensíveis.
- [ ] Nenhum segredo ou credencial foi incluído no código ou no repositório.
- [ ] Documentação de arquitetura, componentes, pipelines ou dependências foi atualizada quando necessário.
- [ ] `poetry run mkdocs build` passou.
- [ ] O PR é pequeno, está descrito e foi submetido à revisão obrigatória.
- [ ] Todas as etapas da CI foram aprovadas.
