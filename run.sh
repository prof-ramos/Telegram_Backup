#!/bin/bash

# 🚀 Telegram Backup Manager - Script de Execução
# Executa a aplicação Streamlit com configurações otimizadas

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funções auxiliares
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    print_warning "Ambiente virtual não encontrado. Execute o script de instalação primeiro."
    echo ""
    echo "Para instalar:"
    echo "  bash install.sh"
    echo ""
    exit 1
fi

# Ativar ambiente virtual
print_info "Ativando ambiente virtual..."
source .venv/bin/activate

# Verificar se Streamlit está instalado
if ! command -v streamlit &>/dev/null; then
    print_error "Streamlit não encontrado. Por favor, execute a instalação primeiro."
    exit 1
fi

# Verificar se o arquivo da aplicação existe
if [ ! -f "streamlit_app.py" ]; then
    print_error "Arquivo streamlit_app.py não encontrado."
    exit 1
fi

# Verificação de segurança de arquivos de sessão
print_info "Verificando permissões de segurança..."
find . -name "*.session" -type f -exec chmod 600 {} \;
print_success "Permissões de arquivos de sessão ajustadas (600)"

# Mensagem de boas-vindas
echo ""
echo "======================================================"
print_success "🚀 Iniciando Telegram Backup Manager"
print_success "Interface Web com Streamlit v2.0"
echo "======================================================"
echo ""
print_info "Configurações:"
print_info "- Porta: 8501"
print_info "- Tema: Sage/Charcoal"
print_info "- Auto-refresh: Ativado"
print_info "- Hot-reload: Ativado"
echo ""
print_info "Acesse: http://localhost:8501"
echo ""
print_warning "Pressione Ctrl+C para parar o servidor"
echo ""

# Executar Streamlit com configurações otimizadas
streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=localhost \
    --server.headless=false \
    --server.runOnSave=true \
    --server.allowRunOnSave=true \
    --browser.gatherUsageStats=false \
    --theme.primaryColor="#5c7359" \
    --theme.backgroundColor="#f6f7f6" \
    --theme.secondaryBackgroundColor="#e3e7e3" \
    --theme.textColor="#3d3d3d"

# Mensagem de encerramento
echo ""
echo "======================================================"
print_success "Aplicação encerrada com sucesso!"
echo "======================================================"