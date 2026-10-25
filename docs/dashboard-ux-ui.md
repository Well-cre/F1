# Relatório de melhorias de UX/UI

## Objetivo

Modernizar o dashboard de Fórmula 1 com uma identidade visual própria, melhor
legibilidade e gráficos interativos, preservando a organização do projeto e a
forma de inicialização existente:

```bash
poetry run streamlit run src/f1/dashboard.py
```

## Alterações realizadas

- **Identidade visual:** tema escuro profissional com vermelho de corrida,
  superfícies em grafite, tipografia sans-serif e cores consistentes para
  gráficos e tabelas.
- **Marca e favicon:** logotipo vetorial "F1 Race Intelligence" na navegação e
  favicon SVG personalizado na aba do navegador.
- **Sidebar e navegação:** navegação vertical com descrições de cada seção,
  marca do projeto, estado recolhível e ação explícita para atualizar os dados.
- **Métricas:** indicadores apresentados em cards com borda e disposição
  horizontal que se adapta a telas menores.
- **Gráficos:** gráficos Plotly interativos para pontuação dos pilotos e
  melhores voltas por circuito, com tema escuro, tooltips e controles visuais
  simplificados.
- **Organização e acessibilidade:** títulos mais claros, tabelas padronizadas,
  descrições alternativas para tabelas e gráficos e manutenção das seções
  Resumo, Sessões, Pilotos, Voltas e Dados brutos.
- **Animação e responsividade:** entrada discreta do conteúdo, realce sutil dos
  cards e respeito à preferência do sistema por movimento reduzido.
- **Desempenho:** cache de dados limitado por quantidade e validade, cache do
  estado derivado e agrupamento prévio de voltas/resultados por sessão para
  evitar varreduras repetidas.
- **Dependências:** Plotly declarado explicitamente no Poetry para que os
  gráficos funcionem em instalações reproduzíveis.

## Arquivos envolvidos

- `src/f1/dashboard.py`: componentes, navegação, visualizações e otimização dos
  cálculos.
- `.streamlit/config.toml`: tema e tokens visuais do Streamlit.
- `src/f1/assets/f1-data-logo.svg` e `src/f1/assets/f1-data-favicon.svg`: marca e
  ícone da aplicação.
- `pyproject.toml` e `poetry.lock`: dependência de Plotly.
- `mkdocs.yml` e `docs/index.md`: inclusão deste relatório na documentação.

## Inicialização e comportamento

O script do dashboard continua sendo o mesmo e não foi introduzida uma nova
estrutura de páginas. A seleção existente mantém as cinco áreas e a coleta de
dados continua separada do processo de visualização.

## Validação

Os 13 testes do projeto passaram sem a coleta de cobertura, os testes específicos
do dashboard passaram, o Ruff não encontrou problemas e a documentação foi
gerada em modo estrito. A execução com a configuração padrão de cobertura
continua abaixo do limite de 50% (44,75%), devido à cobertura global do projeto,
incluindo o módulo `dashboardbackup.py` já existente. A aplicação também foi
iniciada e conferida no navegador usando o comando documentado.
