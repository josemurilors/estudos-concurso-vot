# Quiz Interativo — Cisco / Mikrotik / Linux

Site de quiz com 100 questões de TI (Cisco, Mikrotik e Linux), autenticação de usuário, persistência de respostas e relatório de desempenho.

## Funcionalidades

- Login e cadastro de usuário
- 100 questões divididas em 3 temas
- Respostas persistem mesmo ao navegar entre questões
- Relatório individual com acertos e erros
- Explicação detalhada para cada questão
- Tema AMOLED black
- Botão para limpar todas as respostas

## Tecnologias

- **Backend:** Python + Flask
- **Banco:** SQLite
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Docker:** Dockerfile + docker-compose

## Como Executar

### Local (sem Docker)

```bash
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

### Com Docker

```bash
docker compose up -d
```

Acesse: http://localhost:5000

## Estrutura do Projeto

```
├── app.py              # Servidor Flask
├── database.py         # Modelos e acesso ao SQLite
├── provas.json         # Banco de 100 questões
├── requirements.txt    # Dependências Python
├── Dockerfile          # Imagem Docker
├── docker-compose.yml  # Orquestração Docker
├── templates/          # Templates HTML (Jinja2)
│   ├── login.html
│   ├── cadastro.html
│   ├── quiz.html
│   └── relatorio.html
└── static/
    └── style.css       # Estilo AMOLED black
```

## Estrutura das Questões (JSON)

```json
{
  "id": 1,
  "enunciado": "texto da pergunta",
  "alts": ["alt A", "alt B", "alt C", "alt D", "alt E"],
  "correta": 1,
  "explicacao": "explicação da resposta",
  "tema": "cisco"
}
```
