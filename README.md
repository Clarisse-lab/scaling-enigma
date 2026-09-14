# scaling-enigma

Sistema pessoal para (1) buscar e ranquear vagas de emprego alinhadas ao meu perfil e (2) servir como portfólio para chamar atenção de empresas na interseção **tecnologia + ciência** — análise de dados, automação e sistemas para indústria farmacêutica/life sciences.

## Estrutura do repositório

```
.
├── job_search/       # motor de busca e ranqueamento de vagas
│   ├── config/        # plataformas-alvo e palavras-chave de matching
│   └── src/jobhunter/  # código: fontes de dados, modelo de vaga, matching, CLI
├── resume/            # currículo original + dados estruturados + versões otimizadas por vaga
│   ├── original/       # PDF/Word do currículo-base (não versionar dados sensíveis publicamente)
│   ├── tailored/        # currículos gerados/otimizados para vagas específicas
│   └── resume_data.yaml # currículo estruturado (skills, experiências, keywords) usado no matching
└── portfolio/          # portfólio: README + projetos em destaque
    └── projects/
```

## Como funciona a busca de vagas

Nem toda plataforma pode ser automatizada com segurança — os Termos de Uso de várias delas (LinkedIn, Glassdoor) proíbem scraping e o risco é bloqueio de conta. A estratégia adotada:

- **Automatizado (API/página pública por empresa):** Gupy, Solides, Abler, BairesDev e similares — várias expõem endpoints públicos de listagem de vagas por empresa, sem precisar de login.
- **Manual/assistido:** LinkedIn, Glassdoor — alimentados via alertas de e-mail configurados por você ou links colados manualmente em `job_search/config/manual_jobs.yaml`. O sistema ainda pontua e ranqueia essas vagas junto com as demais.

Ver detalhes de cada fonte em `job_search/src/jobhunter/sources/`.

## Status

🚧 Em construção. Próximos passos:
1. Importar o currículo real em `resume/original/` e preencher `resume/resume_data.yaml`.
2. Validar e completar os endpoints/empresas-alvo em `job_search/config/platforms.yaml`.
3. Rodar o matching e revisar o ranking de vagas.
4. Popular `portfolio/` com projetos reais.
