import os
import sys
import pty
import select
import struct
import fcntl
import termios
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'python-web-ide-secret-key-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR / "workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

# Garantir que main.py exista por padrão
if not (WORKSPACE_DIR / "main.py").exists():
    with open(WORKSPACE_DIR / "main.py", "w", encoding="utf-8") as f:
        f.write('''# Arquivo inicial de exemplo
def saudacao():
    print("=" * 40)
    print("🚀 Bem-vindo ao Python Web IDE!")
    print("=" * 40)
    nome = input("Qual o seu nome? ")
    print(f"\\nOlá, {nome}! Seu ambiente Python está funcionando perfeitamente.\\n")

if __name__ == '__main__':
    saudacao()
''')

# Guardar sessões PTY por sid do cliente
pty_sessions = {}

def get_safe_path(rel_path: str) -> Path:
    """Garante que o caminho requisitado não saia do diretório workspace."""
    clean_path = (WORKSPACE_DIR / rel_path.lstrip("/\\")).resolve()
    if not str(clean_path).startswith(str(WORKSPACE_DIR.resolve())):
        raise ValueError("Acesso fora do diretório de workspace não permitido.")
    return clean_path

def build_file_tree(directory: Path) -> list:
    """Gera a árvore hierárquica de arquivos e pastas recursivamente."""
    items = []
    try:
        entries = sorted(directory.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        for entry in entries:
            if entry.name.startswith('.') or entry.name == '__pycache__':
                continue
            
            rel_path = entry.relative_to(WORKSPACE_DIR).as_posix()
            if entry.is_dir():
                items.append({
                    "name": entry.name,
                    "path": rel_path,
                    "type": "dir",
                    "children": build_file_tree(entry)
                })
            else:
                items.append({
                    "name": entry.name,
                    "path": rel_path,
                    "type": "file"
                })
    except Exception as e:
        print(f"Erro ao ler diretório {directory}: {e}")
    return items

def read_pty_output(sid, master_fd):
    """Lê a saída do PTY continuamente e envia para o frontend via WebSocket."""
    while True:
        try:
            r, _, _ = select.select([master_fd], [], [], 0.1)
            if master_fd in r:
                data = os.read(master_fd, 4096)
                if not data:
                    break
                socketio.emit('pty_output', {
                    'output': data.decode('utf-8', errors='replace')
                }, to=sid)
            else:
                if sid not in pty_sessions or pty_sessions[sid].get('master_fd') != master_fd:
                    break
        except (OSError, Exception):
            break
    
    if sid in pty_sessions and pty_sessions[sid].get('master_fd') == master_fd:
        pty_sessions.pop(sid, None)

@app.route('/')
def index():
    return render_template('index.html')

# === REST Endpoints ===

@app.route('/api/tree', methods=['GET'])
def api_get_tree():
    tree = build_file_tree(WORKSPACE_DIR)
    return jsonify({"success": True, "tree": tree})

@app.route('/api/file', methods=['GET', 'POST'])
def api_file():
    if request.method == 'GET':
        path = request.args.get('path', '')
        try:
            file_path = get_safe_path(path)
            if not file_path.is_file():
                return jsonify({"success": False, "error": "Arquivo não encontrado."}), 404
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return jsonify({"success": True, "path": path, "name": file_path.name, "content": content})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    else:
        data = request.get_json() or {}
        path = data.get('path', '')
        content = data.get('content', '')
        try:
            file_path = get_safe_path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return jsonify({"success": True, "path": path})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/create-file', methods=['POST'])
def api_create_file():
    data = request.get_json() or {}
    path = data.get('path', '').strip()
    if not path:
        return jsonify({"success": False, "error": "Nome do arquivo não pode ser vazio."}), 400
    try:
        file_path = get_safe_path(path)
        if file_path.exists():
            return jsonify({"success": False, "error": "Arquivo já existe."}), 400
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        tree = build_file_tree(WORKSPACE_DIR)
        socketio.emit('tree_data', {'tree': tree})
        return jsonify({"success": True, "path": path, "tree": tree})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/create-folder', methods=['POST'])
def api_create_folder():
    data = request.get_json() or {}
    path = data.get('path', '').strip()
    if not path:
        return jsonify({"success": False, "error": "Nome da pasta não pode ser vazio."}), 400
    try:
        dir_path = get_safe_path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        tree = build_file_tree(WORKSPACE_DIR)
        socketio.emit('tree_data', {'tree': tree})
        return jsonify({"success": True, "path": path, "tree": tree})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# === SocketIO Handlers ===

@socketio.on('get_tree')
def handle_get_tree():
    tree = build_file_tree(WORKSPACE_DIR)
    emit('tree_data', {'tree': tree})

@socketio.on('read_file')
def handle_read_file(data):
    try:
        file_path = get_safe_path(data.get('path', ''))
        if not file_path.is_file():
            emit('error_message', {'message': f'Arquivo não encontrado: {data.get("path")}'})
            return
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        emit('file_content', {
            'path': data.get('path'),
            'name': file_path.name,
            'content': content
        })
    except Exception as e:
        emit('error_message', {'message': str(e)})

@socketio.on('save_file')
def handle_save_file(data):
    try:
        file_path = get_safe_path(data.get('path', ''))
        content = data.get('content', '')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        emit('file_saved', {'path': data.get('path')})
    except Exception as e:
        emit('error_message', {'message': f'Erro ao salvar arquivo: {e}'})

@socketio.on('create_file')
def handle_create_file(data):
    try:
        rel_path = data.get('path', '').strip()
        if not rel_path:
            emit('error_message', {'message': 'Nome do arquivo não pode ser vazio.'})
            return
        
        file_path = get_safe_path(rel_path)
        if file_path.exists():
            emit('error_message', {'message': f'Arquivo ou diretório já existe: {rel_path}'})
            return
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        
        tree = build_file_tree(WORKSPACE_DIR)
        socketio.emit('tree_data', {'tree': tree})
        emit('item_created', {'path': rel_path, 'type': 'file'})
    except Exception as e:
        emit('error_message', {'message': f'Erro ao criar arquivo: {e}'})

@socketio.on('create_directory')
def handle_create_directory(data):
    try:
        rel_path = data.get('path', '').strip()
        if not rel_path:
            emit('error_message', {'message': 'Nome da pasta não pode ser vazio.'})
            return
        
        dir_path = get_safe_path(rel_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        tree = build_file_tree(WORKSPACE_DIR)
        socketio.emit('tree_data', {'tree': tree})
        emit('item_created', {'path': rel_path, 'type': 'dir'})
    except Exception as e:
        emit('error_message', {'message': f'Erro ao criar pasta: {e}'})

@socketio.on('delete_item')
def handle_delete_item(data):
    try:
        rel_path = data.get('path', '').strip()
        if not rel_path:
            return
        target = get_safe_path(rel_path)
        if target.is_dir():
            shutil.rmtree(target)
        elif target.is_file():
            target.unlink()
        
        tree = build_file_tree(WORKSPACE_DIR)
        socketio.emit('tree_data', {'tree': tree})
        emit('item_deleted', {'path': rel_path})
    except Exception as e:
        emit('error_message', {'message': f'Erro ao deletar: {e}'})

@socketio.on('rename_item')
def handle_rename_item(data):
    try:
        old_path = get_safe_path(data.get('old_path', ''))
        new_path = get_safe_path(data.get('new_path', ''))
        
        if not old_path.exists():
            emit('error_message', {'message': 'Item original não encontrado.'})
            return
        
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(new_path)
        
        tree = build_file_tree(WORKSPACE_DIR)
        socketio.emit('tree_data', {'tree': tree})
        emit('item_renamed', {
            'old_path': data.get('old_path'),
            'new_path': data.get('new_path')
        })
    except Exception as e:
        emit('error_message', {'message': f'Erro ao renomear: {e}'})

# === Terminal PTY Interativo ===

@socketio.on('init_pty')
def handle_init_pty():
    sid = request.sid
    if sid in pty_sessions:
        try:
            os.close(pty_sessions[sid]['master_fd'])
        except Exception:
            pass
        pty_sessions.pop(sid, None)

    master_fd, slave_fd = pty.openpty()
    
    shell = os.environ.get('SHELL', '/bin/bash')
    if not os.path.exists(shell):
        shell = '/bin/sh'
    
    pid = os.fork()
    if pid == 0:
        os.setsid()
        os.dup2(slave_fd, 0)
        os.dup2(slave_fd, 1)
        os.dup2(slave_fd, 2)
        os.close(master_fd)
        os.close(slave_fd)
        
        os.chdir(str(WORKSPACE_DIR))
        os.environ['TERM'] = 'xterm-256color'
        os.environ['PS1'] = r'\[\033[01;32m\]python-ide:\[\033[01;34m\]\w\[\033[00m\]\$ '
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.execlp(shell, shell)
    else:
        os.close(slave_fd)
        pty_sessions[sid] = {
            'master_fd': master_fd,
            'pid': pid
        }
        socketio.start_background_task(target=read_pty_output, sid=sid, master_fd=master_fd)
        emit('pty_ready')

@socketio.on('pty_input')
def handle_pty_input(data):
    sid = request.sid
    if sid in pty_sessions:
        master_fd = pty_sessions[sid]['master_fd']
        inp = data.get('input', '')
        try:
            os.write(master_fd, inp.encode('utf-8'))
        except Exception as e:
            print(f"Erro escrevendo no pty: {e}")

@socketio.on('pty_resize')
def handle_pty_resize(data):
    sid = request.sid
    if sid in pty_sessions:
        master_fd = pty_sessions[sid]['master_fd']
        cols = int(data.get('cols', 80))
        rows = int(data.get('rows', 24))
        try:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
        except Exception as e:
            print(f"Erro no redimensionamento do PTY: {e}")

@socketio.on('run_script')
def handle_run_script(data):
    sid = request.sid
    rel_path = data.get('path', '')
    if not rel_path:
        emit('error_message', {'message': 'Nenhum arquivo selecionado para execução.'})
        return
    
    if 'content' in data:
        try:
            file_path = get_safe_path(rel_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data['content'])
        except Exception as e:
            emit('error_message', {'message': f'Erro ao salvar antes de rodar: {e}'})
            return

    if sid in pty_sessions:
        master_fd = pty_sessions[sid]['master_fd']
        cmd = f'python3 "{rel_path}"\n'
        try:
            os.write(master_fd, cmd.encode('utf-8'))
        except Exception as e:
            emit('error_message', {'message': f'Erro ao enviar comando para terminal: {e}'})
    else:
        emit('error_message', {'message': 'Terminal não conectado.'})

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in pty_sessions:
        try:
            os.close(pty_sessions[sid]['master_fd'])
        except Exception:
            pass
        pty_sessions.pop(sid, None)

if __name__ == '__main__':
    print(f"Iniciando Python Web IDE na porta 5000...")
    print(f"Diretório de Workspace: {WORKSPACE_DIR}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
