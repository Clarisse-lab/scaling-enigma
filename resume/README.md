# Currículo

- `original/` — arquivo(s) do currículo-base (PDF/Word). **Não commite dados sensíveis se o repositório for público** (considere deixar essa pasta fora do Git via `.gitignore` se preferir manter o CV privado, e versionar só `resume_data.yaml` sem dados de contato).
- `resume_data.yaml` — currículo estruturado (skills, experiências, formação) usado pelo motor de matching e para gerar versões otimizadas.
- `tailored/` — currículos adaptados para vagas específicas, gerados a partir de `resume_data.yaml` + a descrição da vaga.

## Próximo passo

Assim que o arquivo do currículo for adicionado em `original/`, seus dados devem ser transcritos para `resume_data.yaml` para alimentar o matching automático.
