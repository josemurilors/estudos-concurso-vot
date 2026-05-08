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
- **Token bucket** - rate limiting no login/cadastro (5 tentativas/minuto por IP)
- **Criptografia em repouso** - banco SQLite criptografado via Fernet (AES)

## Tecnologias

- **Backend:** Python + Flask
- **Banco:** SQLite com criptografia Fernet (AES-128)
- **Rate Limiter:** Token bucket puro (sem dependências)
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Docker:** Dockerfile + docker-compose

## Como Executar

### Local (sem Docker)

```bash
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

**Nota:** Na primeira execução, uma chave `db.key` é gerada automaticamente. Ela é usada para criptografar o `database.enc` em disco. Mantenha essa chave em segredo.

### Com Docker

```bash
# Opcional: definir chaves via ambiente (recomendado em produção)
export DB_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

docker compose up -d
```

Acesse: http://localhost:5000

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave de assinatura de sessão Flask | aleatório a cada restart |
| `DB_KEY` | Chave de criptografia do banco (Fernet) | gerada em `db.key` |
| `FLASK_DEBUG` | Modo debug (`1` liga, `0` desliga) | `0` |
| `DATA_DIR` | Diretório para `database.enc` e `db.key` | diretório do `app.py` |

## Segurança

- **Senhas** armazenadas com hash pbkdf2:sha256 (werkzeug)
- **Banco criptografado** em disco via Fernet (AES-128-CBC com HMAC)
- **Rate limiting** via token bucket: 5 tentativas/minuto por IP no login/cadastro
- **XSS** prevenido: explicações são inseridas via `textContent` (DOM puro)
- **SQL Injection** prevenido: todas queries usam placeholders (`?`)

## Estrutura do Projeto

```
├── app.py              # Servidor Flask com rate limiting
├── database.py         # SQLite com criptografia Fernet
├── token_bucket.py     # Rate limiter token bucket
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
