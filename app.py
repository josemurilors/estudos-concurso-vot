import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
from token_bucket import MemoryRateLimiter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())
DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
)

limiter = MemoryRateLimiter()

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), 'provas.json')
db.init_db()

def load_questions():
    with open(QUESTIONS_PATH, encoding='utf-8') as f:
        return json.load(f)

def get_client_ip():
    return request.remote_addr or 'unknown'

def taxa_limite(endpoint, max_tokens=5, period_secs=60):
    ip = get_client_ip()
    key = f'{endpoint}:{ip}'
    rate = max_tokens / period_secs
    bucket = limiter.get_bucket(key, rate=rate, capacity=max_tokens)
    return bucket.consume(1)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('quiz'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not taxa_limite('login'):
            return render_template('login.html', erro='Muitas tentativas. Aguarde 1 minuto.')
        username = request.form['username'].strip()
        password = request.form['password']
        user = db.buscar_usuario(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('quiz'))
        return render_template('login.html', erro='Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        if not taxa_limite('cadastro'):
            return render_template('cadastro.html', erro='Muitas tentativas. Aguarde 1 minuto.')
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            return render_template('cadastro.html', erro='Preencha todos os campos')
        user_id = db.criar_usuario(username, generate_password_hash(password))
        if user_id is None:
            return render_template('cadastro.html', erro='Usuário já existe')
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for('quiz'))
    return render_template('cadastro.html')

@app.route('/quiz')
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    perguntas = load_questions()
    respostas = db.get_respostas(session['user_id'])
    perguntas_seguras = []
    for q in perguntas:
        qs = dict(q)
        qs.pop('correta', None)
        perguntas_seguras.append(qs)
    return render_template('quiz.html', perguntas=perguntas_seguras, respostas=respostas, username=session['username'])

@app.route('/api/responder', methods=['POST'])
def responder():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    data = request.get_json()
    if not data:
        return jsonify({'erro': 'JSON inválido'}), 400
    questao_id = data.get('questao_id')
    resposta_escolhida = data.get('resposta')
    if questao_id is None or resposta_escolhida is None:
        return jsonify({'erro': 'Dados incompletos'}), 400
    perguntas = load_questions()
    questao = next((q for q in perguntas if q['id'] == questao_id), None)
    if not questao:
        return jsonify({'erro': 'Questão não encontrada'}), 404
    if resposta_escolhida < 0:
        db.deletar_resposta(session['user_id'], questao_id)
        return jsonify({'ok': True})
    acertou = 1 if resposta_escolhida == questao['correta'] else 0
    db.salvar_resposta(session['user_id'], questao_id, resposta_escolhida, acertou)
    return jsonify({'acertou': bool(acertou), 'resposta_correta': questao['correta'], 'explicacao': questao['explicacao']})

@app.route('/relatorio')
def relatorio():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    perguntas = load_questions()
    respostas = db.get_respostas(session['user_id'])
    total, acertos = db.get_relatorio(session['user_id'])
    questoes_respondidas = []
    for q in perguntas:
        if q['id'] in respostas:
            questoes_respondidas.append({
                'questao': q,
                'resposta_escolhida': respostas[q['id']]['resposta_escolhida'],
                'acertou': respostas[q['id']]['acertou']
            })
    return render_template('relatorio.html', questoes=questoes_respondidas, total=total, acertos=acertos, username=session['username'])

@app.route('/api/limpar', methods=['POST'])
def limpar():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401
    db.limpar_respostas(session['user_id'])
    return jsonify({'ok': True})

import secrets
import time

@app.route('/resetar', methods=['GET', 'POST'])
def reset_solicitar():
    if request.method == 'POST':
        if not taxa_limite('reset'):
            return render_template('reset_solicitar.html', erro='Muitas tentativas. Aguarde 1 minuto.')
        username = request.form['username'].strip()
        user = db.buscar_usuario(username)
        if user:
            token = secrets.token_urlsafe(32)
            db.salvar_reset_token(user['id'], token)
            return render_template('reset_solicitar.html', token=token, username=username)
        return render_template('reset_solicitar.html', erro='Usuário não encontrado')
    return render_template('reset_solicitar.html')

@app.route('/resetar/<token>', methods=['GET', 'POST'])
def reset_confirmar(token):
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not password:
            return render_template('reset_confirmar.html', token=token, erro='Informe a nova senha')
        user = db.buscar_usuario(username)
        if not user:
            return render_template('reset_confirmar.html', token=token, erro='Usuário não encontrado')
        stored = db.buscar_reset_token(user['id'], token)
        if not stored:
            return render_template('reset_confirmar.html', token=token, erro='Token inválido ou expirado')
        db.atualizar_senha(user['id'], generate_password_hash(password))
        db.deletar_reset_token(user['id'])
        return redirect(url_for('login'))
    return render_template('reset_confirmar.html', token=token)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
