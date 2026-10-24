# OpenF1 API — resumo

Resumo dos principais recursos da [documentação oficial da OpenF1](https://openf1.org/docs/#api-endpoints). A API fornece dados de Fórmula 1 em JSON ou CSV.

## Acesso e URL base

- URL base: `https://api.openf1.org/v1/`
- Os dados históricos (a partir de 2023) são gratuitos e não exigem autenticação.
- O acesso a dados em tempo real exige uma assinatura paga.
- Cada recurso é consultado por uma requisição HTTP GET; por exemplo, `/sessions` ou `/laps`.

## Principais endpoints

| Endpoint | O que retorna |
| --- | --- |
| `/meetings` | Etapas e eventos do calendário, com país, circuito, datas e identificadores. |
| `/sessions` | Sessões de uma etapa, como treinos, classificação, sprint e corrida. |
| `/drivers` | Informações dos pilotos participantes de uma sessão. |
| `/car_data` | Telemetria do carro, incluindo velocidade, RPM, marcha, acelerador, freio e DRS. |
| `/location` | Posição aproximada do carro no circuito. |
| `/laps` | Voltas, tempos totais e por setor, velocidades de referência e mini setores. |
| `/intervals` | Intervalos de tempo ou distância entre pilotos durante a sessão. |
| `/position` | Mudanças de posição dos pilotos ao longo da sessão. |
| `/pit` | Registros de entrada e saída dos boxes e duração da parada. |
| `/stints` | Stints dos pilotos, voltas inicial e final e composto/idade dos pneus. |
| `/race_control` | Mensagens de direção de prova, como bandeiras, incidentes e notificações. |
| `/team_radio` | Links para gravações de rádio disponíveis; a coleção não contém todas as comunicações. |
| `/weather` | Condições meteorológicas no circuito, atualizadas a cada minuto. |
| `/overtakes` | Registros de ultrapassagens e posições envolvidas. |
| `/starting_grid` | Posições de largada dos pilotos. |
| `/session_result` | Resultados e classificação final da sessão; pode aparecer alguns minutos após a publicação oficial. |
| `/championship_drivers` | Pontuação e posição no campeonato de pilotos. Recurso beta, disponível apenas para sessões de corrida. |
| `/championship_teams` | Pontuação e posição no campeonato de equipes. Recurso beta, disponível apenas para sessões de corrida. |

Os campos retornados variam conforme o endpoint. Consulte a seção **Attributes** de cada recurso na documentação oficial para conhecer o esquema completo.

## Filtros e identificadores

Os filtros são enviados como parâmetros de consulta. É comum combinar identificadores e campos específicos para restringir os resultados:

```text
https://api.openf1.org/v1/laps?session_key=9158&driver_number=44&lap_number=10
```

- `session_key` identifica uma sessão; `meeting_key` identifica uma etapa. Muitos endpoints aceitam um ou ambos.
- `driver_number` identifica o piloto.
- Campos de data permitem limitar os resultados a um período. A API aceita operadores de comparação, como `>`, `>=`, `<` e `<=`.
- Codifique caracteres especiais na URL quando necessário. Por exemplo, `<` pode ser enviado como `%3C`.
- O valor `latest` pode ser usado em `session_key` ou `meeting_key` nos endpoints que documentam esse suporte.

## Respostas e formatos

- JSON é o formato padrão; normalmente a resposta é uma lista de objetos.
- Para CSV, adicione `csv=true` à consulta.
- Datas e horários são fornecidos em UTC e geralmente usam o formato ISO 8601.
- Endpoints de telemetria e localização podem retornar muitos registros. Use filtros de sessão, piloto e intervalo de tempo para reduzir a resposta.

Exemplo simples com `curl`:

```bash
curl "https://api.openf1.org/v1/sessions?year=2023&country_name=Belgium"
```

## Observações

- `car_data` e `location` têm amostragem aproximada de 3,7 Hz; a posição é aproximada e não indica se o carro está à esquerda ou à direita da pista.
- Os dados de `weather` são atualizados a cada minuto.
- `team_radio` contém apenas uma seleção das comunicações.
- Alguns recursos, como os endpoints de campeonato, estão marcados como beta na documentação.

---

Fonte: [OpenF1 — API endpoints](https://openf1.org/docs/#api-endpoints). Consultado em 23/10/2026.
