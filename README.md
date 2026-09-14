# scaling-enigma

Motor pessoal de busca e ranqueamento de vagas de emprego, focado na interseção **tecnologia + ciência** — análise de dados, automação e sistemas para indústria farmacêutica/life sciences.

> O portfólio para chamar atenção de recrutadores vive em um repositório separado (ver seção "Portfólio" abaixo).

## Estrutura do repositório

```
.
├── job_search/       # motor de busca e ranqueamento de vagas
│   ├── config/        # plataformas-alvo e palavras-chave de matching
│   └── src/jobhunter/  # código: fontes de dados, modelo de vaga, matching, CLI
└── resume/            # currículo original + dados estruturados + versões otimizadas por vaga
    ├── original/       # PDF/Word do currículo-base (não versionar dados sensíveis publicamente)
    ├── tailored/        # currículos gerados/otimizados para vagas específicas
    └── resume_data.yaml # currículo estruturado (skills, experiências, keywords) usado no matching
```

## Como funciona a busca de vagas

Nem toda plataforma pode ser automatizada com segurança — os Termos de Uso de várias delas (LinkedIn, Glassdoor) proíbem scraping e o risco é bloqueio de conta. A estratégia adotada:

- **Automatizado (API/página pública por empresa):** Gupy, Solides, Abler, BairesDev e similares — várias expõem endpoints públicos de listagem de vagas por empresa, sem precisar de login.
- **Manual/assistido:** LinkedIn, Glassdoor — alimentados via alertas de e-mail configurados por você ou links colados manualmente em `job_search/config/manual_jobs.yaml`. O sistema ainda pontua e ranqueia essas vagas junto com as demais.

Ver detalhes de cada fonte em `job_search/src/jobhunter/sources/`.

## Portfólio

O portfólio (site/repositório para atrair recrutadores) é um projeto separado, ainda a ser definido/criado em outro repositório.

## Status

🚧 Em construção.

✅ Feito:
- `resume/resume_data.yaml` preenchido com o currículo real (farmacêutica + gestora de tecnologia, foco em automação/dados/cloud para healthtech/SaaS/farma).
- `job_search/config/keywords.yaml` recalibrado com base nesse perfil.
- Matching testado e funcionando (`python -m jobhunter.cli`).

⏳ Pendente:
1. Lista de empresas-alvo (farmacêuticas, laboratórios, healthtech) em `job_search/config/platforms.yaml`, para eu validar os endpoints reais de Gupy/Solides/Abler/BairesDev.
2. Definir se o PDF original vai para `resume/original/` (contém telefone — ver `resume/README.md` sobre exposição de dados sensíveis caso o repositório seja público).
