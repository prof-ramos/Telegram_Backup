#!/bin/bash

# 🚀 Telegram Backup Manager - Instalador UV
# Script de instalação automatizado para o Telegram Backup Manager v2.0

set -e

echo "🚀 Iniciando instalação do Telegram Backup Manager v2.0"
echo "======================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar sistema operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    CYGWIN*)    PLATFORM=Cygwin;;
    MINGW*)     PLATFORM=MinGw;;
    MSYS*)      PLATFORM=MSYS;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

print_info "Sistema detectado: ${PLATFORM}"

# Verificar Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python 3 encontrado: ${PYTHON_VERSION}"
else
    print_error "Python 3 não encontrado. Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

# Verificar versão do Python
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "${PYTHON_MAJOR}" -lt 3 ] || [ "${PYTHON_MAJOR}" -eq 3 -a "${PYTHON_MINOR}" -lt 8 ]; then
    print_error "Python 3.8 ou superior é necessário. Versão encontrada: ${PYTHON_VERSION}"
    exit 1
fi

# Instalar UV
print_info "Instalando UV (gerenciador de pacotes)..."

if command -v uv &>/dev/null; then
    print_success "UV já está instalado"
else
    case "${PLATFORM}" in
        Linux|Mac)
            print_info "Instalando UV via curl..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
            
            # Adicionar ao PATH
            if [ -f "$HOME/.cargo/bin/uv" ]; then
                echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.bashrc"
                export PATH="$HOME/.cargo/bin:$PATH"
                print_success "UV instalado e adicionado ao PATH"
            fi
            ;;
        CYGWIN|MinGw|MSYS)
            print_info "Instalando UV via PowerShell..."
            powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
            ;;
        *)
            print_warning "Plataforma não reconhecida. Instale UV manualmente:"
            print_info "https://github.com/astral-sh/uv#installation"
            exit 1
            ;;
    esac
fi

# Verificar instalação do UV
if command -v uv &>/dev/null; then
    UV_VERSION=$(uv --version)
    print_success "UV instalado com sucesso: ${UV_VERSION}"
else
    print_error "UV não pôde ser instalado. Por favor, instale manualmente."
    exit 1
fi

# Criar ambiente virtual
print_info "Criando ambiente virtual..."
uv venv

# Ativar ambiente virtual
print_info "Ativando ambiente virtual..."
case "${PLATFORM}" in
    Linux|Mac)
        source .venv/bin/activate
        ;;
    CYGWIN|MinGw|MSYS)
        .venv\\Scripts\\activate
        ;;
esac

# Instalar dependências
print_info "Instalando dependências..."
uv pip install -r requirements.txt

print_success "Dependências instaladas com sucesso!"

# Criar configuração inicial
print_info "Criando configuração inicial..."

# Criar config.env exemplo
if [ ! -f "config.env" ]; then
    cat > config.env << EOF
# Configurações da API do Telegram
API_ID=sua_api_id_aqui
API_HASH=sua_api_hash_aqui
SESSION_NAME=backup_session

# Configurações opcionais
LOG_LEVEL=INFO
MAX_WORKERS=4
REFRESH_INTERVAL=30
EOF
    print_success "Arquivo config.env criado com exemplo"
else
    print_info "Arquivo config.env já existe"
fi

# Criar diretórios necessários
mkdir -p logs
mkdir -p backups

print_success "Estrutura de diretórios criada!"

# Testar instalação
print_info "Testando instalação..."
python3 -c "import streamlit; print('Streamlit importado com sucesso')"
python3 -c "import telethon; print('Telethon importado com sucesso')"
python3 -c "import pandas; print('Pandas importado com sucesso')"

print_success "Todos os módulos foram importados com sucesso!"

# Mensagem final
echo ""
echo "======================================================"
print_success "🎉 Instalação concluída com sucesso!"
echo ""
print_info "Próximos passos:"
echo ""
echo "1. Configure suas credenciais do Telegram:"
echo "   - Edite o arquivo config.env"
echo "   - Adicione seu API_ID e API_HASH"
echo "   - Obtenha as credenciais em: https://my.telegram.org"
echo ""
echo "2. Inicie a aplicação web:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "3. Acesse no navegador:"
echo "   http://localhost:8501"
echo ""
echo "4. Configure suas rotas e filtros na interface web"
echo ""
print_warning "Importante: Nunca compartilhe suas credenciais do Telegram!"
echo "======================================================"

# Oferecer para abrir a aplicação
read -p "Deseja iniciar a aplicação agora? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_info "Iniciando aplicação..."
    streamlit run streamlit_app.py
fi