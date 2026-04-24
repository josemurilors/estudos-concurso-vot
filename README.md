# Prova Interativa Cisco/Mikrotik/Linux (JSON)

Resumo
- Prova interativa em HTML que carrega questões a partir de provas.json (via JSON).
- Possui 34 questões reais já preenchidas e placeholders para as 66 restantes.
- Front-end dinâmico: mostra explicação ao selecionar, navega entre perguntas e gera um relatório.

Arquivos Principais
- index.html: página que carrega questões via JSON.
- provas.json: perguntas (34 reais + placeholders para 66).
- provas_restantes.json (opcional): perguntas adicionais para mesclar.
- assets/: conteúdo estático futuro.

Estrutura de Perguntas (JSON)
- id: identificador da pergunta.
- enunciado: texto da questão (quebras de linha OK).
- alts: array com 5 alternativas (A–E).
- correta: índice da alternativa correta (0-4).
- explicacao: explicação da resposta.
- tema: categoria (cisco, mikrotik, linux).

Como Executar Localmente
- Servir com Python (recomendado):
  - python -m http.server 8000
  - Acesse http://localhost:8000/
- Ou use um servidor estático de sua preferência.

Preenchimento das 66 Questões Adicionais
- Opção A: preencher 35-100 dentro de provas.json no mesmo formato.
- Opção B: usar provas_restantes.json e mesclar no carregamento.

Notas
- A arquitetura facilita adicionar conteúdo futuro sem mexer no front-end.
- Posso fornecer scripts para gerar placeholders automaticamente se desejar.

Contribuição
- Pull requests são bem-vindos.

Licença
- MIT (ou licença de sua escolha).
