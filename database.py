import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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

def get_relatorio(user_id):
    conn = get_conn()
    total = conn.execute('SELECT COUNT(*) as t FROM respostas WHERE user_id = ?', (user_id,)).fetchone()['t']
    acertos = conn.execute('SELECT COUNT(*) as t FROM respostas WHERE user_id = ? AND acertou = 1', (user_id,)).fetchone()['t']
    conn.close()
    return total, acertos
