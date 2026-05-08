import sqlite3
import os
import time
import atexit
from cryptography.fernet import Fernet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', BASE_DIR)
DB_PATH = os.path.join(DATA_DIR, 'database.db')
ENC_PATH = os.path.join(DATA_DIR, 'database.enc')
KEY_PATH = os.path.join(DATA_DIR, 'db.key')

_fernet = None

def _get_key():
    env_key = os.environ.get('DB_KEY')
    if env_key:
        return env_key.encode() if isinstance(env_key, str) else env_key
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, 'rb') as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_PATH, 'wb') as f:
        f.write(key)
    return key

def _get_fernet():
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_get_key())
    return _fernet

def decrypt_db():
    if not os.path.exists(ENC_PATH):
        return
    f = _get_fernet()
    with open(ENC_PATH, 'rb') as src:
        data = f.decrypt(src.read())
    with open(DB_PATH, 'wb') as dst:
        dst.write(data)

def encrypt_db():
    if not os.path.exists(DB_PATH):
        return
    f = _get_fernet()
    with open(DB_PATH, 'rb') as src:
        data = f.encrypt(src.read())
    with open(ENC_PATH, 'wb') as dst:
        dst.write(data)
    os.remove(DB_PATH)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    decrypt_db()
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            questao_id INTEGER NOT NULL,
            resposta_escolhida INTEGER,
            acertou INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, questao_id)
        )
    ''')
    conn.commit()
    conn.close()
    atexit.register(encrypt_db)

def criar_usuario(username, password_hash):
    conn = get_conn()
    try:
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                     (username, password_hash))
        conn.commit()
        return conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()['id']
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def buscar_usuario(username):
    conn = get_conn()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def salvar_resposta(user_id, questao_id, resposta_escolhida, acertou):
    conn = get_conn()
    conn.execute('''
        INSERT OR REPLACE INTO respostas (user_id, questao_id, resposta_escolhida, acertou)
        VALUES (?, ?, ?, ?)
    ''', (user_id, questao_id, resposta_escolhida, acertou))
    conn.commit()
    conn.close()

def get_respostas(user_id):
    conn = get_conn()
    rows = conn.execute('SELECT * FROM respostas WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return {r['questao_id']: {'resposta_escolhida': r['resposta_escolhida'], 'acertou': r['acertou']} for r in rows}

def deletar_resposta(user_id, questao_id):
    conn = get_conn()
    conn.execute('DELETE FROM respostas WHERE user_id = ? AND questao_id = ?', (user_id, questao_id))
    conn.commit()
    conn.close()

def limpar_respostas(user_id):
    conn = get_conn()
    conn.execute('DELETE FROM respostas WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def salvar_reset_token(user_id, token, expira_em=3600):
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            expira INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('DELETE FROM reset_tokens WHERE user_id = ?', (user_id,))
    conn.execute('INSERT INTO reset_tokens (user_id, token, expira) VALUES (?, ?, ?)',
                 (user_id, token, int(time.time()) + expira_em))
    conn.commit()
    conn.close()

def buscar_reset_token(user_id, token):
    conn = get_conn()
    row = conn.execute(
        'SELECT * FROM reset_tokens WHERE user_id = ? AND token = ? AND expira > ?',
        (user_id, token, int(time.time()))
    ).fetchone()
    conn.close()
    return row

def deletar_reset_token(user_id):
    conn = get_conn()
    conn.execute('DELETE FROM reset_tokens WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def atualizar_senha(user_id, password_hash):
    conn = get_conn()
    conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()

def get_relatorio(user_id):
    conn = get_conn()
    total = conn.execute('SELECT COUNT(*) as t FROM respostas WHERE user_id = ?', (user_id,)).fetchone()['t']
    acertos = conn.execute('SELECT COUNT(*) as t FROM respostas WHERE user_id = ? AND acertou = 1', (user_id,)).fetchone()['t']
    conn.close()
    return total, acertos
