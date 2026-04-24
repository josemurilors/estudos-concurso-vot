# Prova Interativa Cisco/Mikrotik/Linux (JSON)

Resumo
- Prova interativa em HTML que carrega questões a partir de provas.json (via JSON).
- 34 questões reais já preenchidas e placeholders para as 66 restantes.
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
- Sem Docker (teste rápido):
  - python -m http.server 8000
  - Acesse http://localhost:8000/
- Com Docker Compose (recomendado para produção/local):
  - Build: docker-compose build
  - Run: docker-compose up -d
  - Acesse: http://localhost:8080/

Dockerization com diretório externo (facilita edição de conteúdo)
- Opcional: mapear um diretório externo com conteúdo do site para o contêiner nginx.
- Estrutura sugerida de diretório externo: site/ (contém index.html, provas.json e provas_restantes.json).
- Compose usa: ./site:/usr/share/nginx/html:ro para facilitar atualizações sem rebuild.

Contribuição
- Pull requests são bem-vindos.

Licença
- MIT (ou a licença de sua escolha).

Notas rápidas
- A abordagem com JSON facilita a expansão para as 100 questões sem mexer no frontend.
- Se desejar, posso incluir scripts para gerar placeholders automaticamente.
