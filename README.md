# Python-Web-IDE

[English](#english) | [Português](#português)

---

## English

A lightweight, web-based Integrated Development Environment (IDE) for writing and running Python code directly in your browser. This project uses Flask for the backend and provides a clean, responsive interface for coding on the go.

### Features

- **Web-Based Interface**: Access your development environment from any browser without local setup.
- **Python Execution**: Write and execute Python scripts with real-time output in an integrated terminal.
- **File Management**: Create, edit, rename, and delete files and nested folders through an interactive workspace tree.
- **Containerized**: Easy to deploy and run using Docker and Docker Compose.

### Technology Stack

- **Backend**: Python 3.12 with Flask and Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript, CodeMirror, and xterm.js
- **Deployment**: Docker and Docker Compose

### Getting Started

#### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.12+ and pip (for local development)

#### Running with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/efrj/Python-Web-IDE.git
   cd Python-Web-IDE
   ```

2. Build and run the container:
   ```bash
   docker compose up --build
   ```

3. Open your browser and access:
   ```text
   http://localhost:5000
   ```

#### Running Locally (without Docker)

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/efrj/Python-Web-IDE.git
   cd Python-Web-IDE
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```bash
   python3 app.py
   ```

4. Open your browser and navigate to:
   ```text
   http://localhost:5000
   ```

### Project Structure

```text
Python-Web-IDE/
├── app.py              # Main Flask and SocketIO application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image configuration
├── docker-compose.yaml # Docker Compose configuration
├── templates/          # Frontend HTML templates
│   └── index.html      # IDE user interface (CodeMirror + xterm.js)
├── workspace/          # Working directory for user files and scripts
└── README.md           # Project documentation
```

### Future Enhancements

- Support for multiple programming languages.
- User authentication and persistent user workspaces.
- Advanced editor features (LSP support, autocompletion, multiple tabs).
- Version control integration (Git).

### License

This project is open-source and available under the MIT License.

### Author

[efrj](https://github.com/efrj)

---

## Português

Um Ambiente de Desenvolvimento Integrado (IDE) leve e baseado na web para escrever e executar código Python diretamente no seu navegador. Este projeto utiliza Flask no backend e oferece uma interface limpa e responsiva para programar em qualquer lugar.

### Funcionalidades

- **Interface Web**: Acesse seu ambiente de desenvolvimento pelo navegador sem necessidade de configuração local.
- **Execução Python**: Escreva e execute scripts Python com saída e interação em tempo real através de terminal integrado.
- **Gerenciamento de Arquivos**: Crie, edite, renomeie e exclua arquivos e pastas aninhadas através do explorador de workspace em árvore.
- **Containerizado**: Fácil de implantar e executar utilizando Docker e Docker Compose.

### Pilha de Tecnologias

- **Backend**: Python 3.12 com Flask e Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript, CodeMirror e xterm.js
- **Implantação**: Docker e Docker Compose

### Como Começar

#### Pré-requisitos

- Docker e Docker Compose (recomendado)
- OU Python 3.12+ e pip (para desenvolvimento local)

#### Executando com Docker (Recomendado)

1. Clone o repositório:
   ```bash
   git clone https://github.com/efrj/Python-Web-IDE.git
   cd Python-Web-IDE
   ```

2. Construa e execute o container:
   ```bash
   docker compose up --build
   ```

3. Abra o navegador e acesse:
   ```text
   http://localhost:5000
   ```

#### Executando Localmente (sem Docker)

1. Clone o repositório e acesse o diretório do projeto:
   ```bash
   git clone https://github.com/efrj/Python-Web-IDE.git
   cd Python-Web-IDE
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Execute a aplicação Flask:
   ```bash
   python3 app.py
   ```

4. Abra o navegador e acesse:
   ```text
   http://localhost:5000
   ```

### Estrutura do Projeto

```text
Python-Web-IDE/
├── app.py              # Aplicação principal Flask e SocketIO
├── requirements.txt    # Dependências Python
├── Dockerfile          # Configuração da imagem Docker
├── docker-compose.yaml # Configuração do Docker Compose
├── templates/          # Templates HTML do frontend
│   └── index.html      # Interface do IDE (CodeMirror + xterm.js)
├── workspace/          # Diretório de trabalho para arquivos do usuário
└── README.md           # Documentação do projeto
```

### Melhorias Futuras

- Suporte para múltiplas linguagens de programação.
- Autenticação de usuários e múltiplos workspaces persistentes.
- Recursos avançados de edição (suporte a LSP, autocompletar, múltiplas abas).
- Integração com controle de versão (Git).

### Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

### Autor

[efrj](https://github.com/efrj)