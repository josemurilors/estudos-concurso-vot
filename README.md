# Prova Interativa Cisco/Mikrotik/Linux (JSON)

Resumo
- Prova interativa em HTML que carrega questões a partir de provas.json (via JSON).
- 100 questões totais (34 Cisco + 33 Mikrotik + 33 Linux).
- Front-end dinâmico: mostra explicação ao selecionar, navega entre perguntas e gera relatório de desempenho por tema.

Arquivos Principais
- index.html: página que carrega questões via JSON.
- provas.json: banco com as 100 questões.
- Dockerfile / docker-compose.yml: configuração Docker com Nginx.
- .dockerignore: arquivos ignorados no build.

Estrutura de Perguntas (JSON)
- id: identificador da pergunta.
- enunciado: texto da questão.
- alts: array com 5 alternativas (A–E).
- correta: índice da alternativa correta (0-4).
- explicacao: explicação da resposta.
- tema: categoria (cisco, mikrotik, linux).

Como Executar Localmente

## Sem Servidor (teste rápido)
```bash
python -m http.server 8000
```
Acesse: http://localhost:8000

## Com Docker (recomendado)
```bash
docker-compose up -d
```
Acesse: http://localhost:8080

## Com Flask (opcional)
```bash
python app.py
```
Acesse: http://localhost:5000

Docker
- Build: `docker build -t provas-prova:latest .`
- Run: `docker run -d -p 8080:80 provas-prova:latest`
- Compose: `docker-compose up -d`

Notas
- O JSON contém 100 questões válidas prontas para uso.
- A arsitea com JSON permite fácil atualização de conteúdo sem mexer no frontend.
- Para adicionar novas questões, edite provas.json mantendo a mesma estrutura.