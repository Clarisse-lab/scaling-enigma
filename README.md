# scaling-enigma

Motor pessoal de busca e ranqueamento de vagas de emprego, focado na interseção **tecnologia + ciência** — análise de dados, automação e sistemas para indústria farmacêutica/life sciences. Roda uma **varredura diária automática** (GitHub Actions) e te notifica quando encontra vagas relevantes.

> O portfólio para chamar atenção de recrutadores vive em um repositório separado.

## Estrutura do repositório

```
.
├── .github/workflows/
│   └── daily-job-scan.yml  # cron diário: busca, pontua, commita relatório, abre issue
├── job_search/
│   ├── config/
│   │   ├── search.yaml       # consultas por área/palavra-chave (Adzuna/Jooble) — sem empresa fixa
│   │   ├── keywords.yaml     # termos usados para pontuar/ranquear as vagas encontradas
│   │   ├── platforms.yaml    # fontes por empresa específica (opcional, ver abaixo)
│   │   └── manual_jobs.yaml  # vagas coladas manualmente (LinkedIn/Glassdoor)
│   ├── results/               # relatórios diários em Markdown (um arquivo por data)
│   ├── src/jobhunter/          # código: fontes de dados, matching, CLI
│   └── .env.example            # chaves de API necessárias
└── resume/
    ├── original/       # PDF/Word do currículo-base
    ├── tailored/        # currículos gerados/otimizados para vagas específicas
    └── resume_data.yaml # currículo estruturado (skills, experiências) usado no matching
```

## Como funciona a busca de vagas

Nem toda plataforma pode ser automatizada com segurança — os Termos de Uso de várias delas (LinkedIn, Glassdoor) proíbem scraping e o risco é bloqueio de conta. Além disso, plataformas como Gupy/Solides/Abler não têm um agregador público de busca por área entre todas as empresas — só por empresa individual, o que não escala. A estratégia adotada:

- **Busca diária por área (sem empresa fixa):** [Adzuna](https://developer.adzuna.com/) e [Jooble](https://jooble.org/api/about) — agregadores com API gratuita de busca por palavra-chave + localização, configurados em `job_search/config/search.yaml`. É a fonte principal da varredura diária.
- **Upwork (freelance/contrato) — desativado:** `job_search/src/jobhunter/sources/upwork.py` tenta o feed RSS público de busca, mas confirmado em execução real (17-18/09) que retorna 403 Forbidden em toda consulta — o Upwork bloqueia acesso sem login. `include_upwork: false` em `search.yaml` por padrão. Reativar só valeria com a API OAuth2 completa (app aprovado + login manual por conta), bem mais trabalho que Adzuna/Jooble.
- **Por empresa específica (opcional):** Gupy, Solides, Abler, BairesDev — se você quiser mirar uma empresa que já conhece, adicione o slug dela em `job_search/config/platforms.yaml`. Os endpoints ainda não foram validados ao vivo (ver notas em cada arquivo de `sources/`).
- **Manual/assistido:** LinkedIn, Glassdoor — sem automação segura; configure um alerta de vaga (Job Alert) por palavra-chave nessas plataformas e cole as relevantes em `job_search/config/manual_jobs.yaml`. Entram no ranking junto com as demais.

Todas as vagas coletadas passam pelo mesmo ranqueamento, definido por `job_search/config/keywords.yaml` (calibrado com base no currículo real em `resume/resume_data.yaml`).

### Vagas remotas

Duas tentativas testadas e descartadas, documentadas aqui pra não repetir o erro:

1. Acrescentar "remoto" no texto da consulta antes de mandar pro Adzuna/Jooble — as APIs tratam como termo obrigatório extra e o resultado quase zera (caiu de 30 vagas pra 0).
2. Filtro rígido pós-busca, descartando qualquer vaga cujo texto não citasse "remoto" (`job_search/config/search.yaml` → `remote_only: true`, lógica em `job_search/src/jobhunter/filters.py`) — o Adzuna geralmente devolve só um trecho curto da descrição, então muita vaga remota de verdade não menciona a palavra nesse trecho. Na prática descartou 92 de 95 vagas reais, sobrando só ruído.

**Abordagem atual:** em vez de excluir, impulsionar. `job_search/config/keywords.yaml` tem a categoria `work_mode`, com pontuação extra para termos como "100% remoto"/"home office" e pontuação negativa para "presencial"/"híbrido". As vagas remotas sobem pro topo do ranking sem que o resto desapareça. `remote_only` continua existindo em `search.yaml` (desativado por padrão) pra quem quiser a exclusão rígida mesmo sabendo da perda de recall.

## Varredura diária automática

O workflow `.github/workflows/daily-job-scan.yml` roda todo dia às 08:00 (horário de Brasília):
1. Executa a busca (Adzuna + Jooble + Upwork + fontes opcionais + manuais).
2. Gera um relatório em `job_search/results/AAAA-MM-DD.md` e commita no repositório.
3. Se houver vagas encontradas, abre uma **Issue** no GitHub com o resumo — isso dispara a notificação padrão do GitHub (e-mail/app) sem precisar configurar nenhum serviço externo.

### Configuração necessária

Para a varredura funcionar, cadastre-se gratuitamente e adicione as chaves como **Secrets** do repositório (Settings → Secrets and variables → Actions):

| Secret | Onde obter |
|---|---|
| `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` | https://developer.adzuna.com/ |
| `JOOBLE_API_KEY` | https://jooble.org/api/about |

Sem essas chaves, a varredura roda mas não encontra vagas (as fontes avisam e pulam, sem quebrar).

Para rodar localmente: copie `job_search/.env.example` para `.env`, preencha as chaves, exporte as variáveis e rode `cd job_search && PYTHONPATH=src python -m jobhunter.cli`.

⚠️ Os endpoints do Adzuna/Jooble foram implementados conforme a documentação pública deles, mas não puderam ser testados ao vivo no ambiente onde este código foi escrito (sem acesso à internet aberta). Acompanhe a primeira execução real no GitHub Actions para confirmar que estão retornando vagas.

## Portfólio

O portfólio (site/repositório para atrair recrutadores) é um projeto separado, ainda a ser definido/criado em outro repositório.

## Status

🚧 Em construção.

✅ Feito:
- `resume/resume_data.yaml` preenchido com o currículo real.
- `job_search/config/keywords.yaml` calibrado com base nesse perfil.
- Busca por área via Adzuna + Jooble implementada (`job_search/config/search.yaml`).
- Varredura diária + notificação via Issue configurada em `.github/workflows/daily-job-scan.yml`.
- Matching testado localmente (sem rede) e funcionando.

⏳ Pendente:
1. Cadastrar nas APIs (Adzuna, Jooble) e configurar os Secrets no GitHub.
2. Acompanhar a primeira execução do workflow para validar os endpoints reais.
3. Definir se o PDF original vai para `resume/original/` (contém telefone — ver `resume/README.md` sobre exposição de dados sensíveis caso o repositório seja público).
