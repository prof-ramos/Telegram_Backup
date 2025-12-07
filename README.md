# 🚀 Telegram Backup Manager v2.0

Sistema profissional de backup para Telegram com interface web moderna usando Streamlit e gerenciamento de dependências com UV.

## ✨ Novidades da v2.0

- 🌐 **Interface Web Moderna**: Nova interface Streamlit com design responsivo
- 📦 **Gerenciador UV**: Migração para o moderno gerenciador de pacotes UV
- 🎨 **Design Aprimorado**: Interface visual com cores, animações e UX melhorada
- 📊 **Dashboard Interativo**: Métricas em tempo real e controle visual
- ⚡ **Performance Otimizada**: Carregamento rápido e operações assíncronas

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Streamlit**: Framework web para interface interativa
- **UV**: Gerenciador moderno de pacotes Python
- **Telethon**: Biblioteca para automação do Telegram
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas
- **Rich**: Interface CLI colorida (mantida para compatibilidade)

## 📦 Instalação com UV

### 1. Instalar UV

```bash
# Usando pip
pip install uv

# Ou usando curl (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou usando PowerShell (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clonar o Repositório

```bash
git clone https://github.com/telegram-backup/telegram-backup-manager.git
cd telegram-backup-manager
```

### 3. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
uv venv

# Ativar ambiente virtual
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 4. Instalar Dependências

```bash
# Instalar dependências principais
uv pip install -r requirements.txt

# Ou instalar diretamente do pyproject.toml
uv pip install -e .
```

### 5. Configurar API do Telegram

Crie o arquivo `config.env` com suas credenciais:

```env
API_ID=sua_api_id
API_HASH=sua_api_hash
SESSION_NAME=backup_session
```

> **⚠️ Importante**: Obtenha suas credenciais em [my.telegram.org](https://my.telegram.org)

## 🚀 Como Usar

### Interface Web (Streamlit)

```bash
# Iniciar aplicação web
streamlit run streamlit_app.py

# Ou usando o script configurado
telegram-backup-web
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

### Interface CLI (Legacy)

```bash
# Menu interativo (mantido para compatibilidade)
python backup_cli.py menu

# Comandos diretos
python backup_cli.py show-config
python backup_cli.py add-route
python backup_cli.py run
```

## 📱 Interface Web

### Dashboard Principal
- 📊 **Métricas em Tempo Real**: Visualize status do sistema
- 🎮 **Controle Rápido**: Inicie, pause ou reinicie o serviço
- 📈 **Estatísticas**: Acompanhe mensagens processadas e rotas ativas

### Gerenciamento de Rotas
- ➕ **Adicionar Rotas**: Interface formulário para novas rotas
- ❌ **Remover Rotas**: Seleção visual para exclusão
- 📋 **Visualizar Rotas**: Tabela com todas as rotas configuradas

### Configuração de Filtros
- 🎯 **Filtros de Conteúdo**: Configure mídia, fotos e vídeos
- ⚙️ **Opções Avançadas**: Media only e outros filtros
- 💾 **Salvar Configurações**: Persistência automática

### Monitoramento
- 📋 **Logs em Tempo Real**: Acompanhe operações do sistema
- 🔍 **Status Detalhado**: Verifique saúde dos componentes
- 📊 **Dashboard Interativo**: Gráficos e visualizações

## 🎯 Funcionalidades Principais

### Backup em Tempo Real
- Monitoramento contínuo de chats
- Encaminhamento automático de mensagens
- Processamento assíncrono e eficiente

### Filtros Inteligentes
- Filtro por tipo de mídia (fotos, vídeos, documentos)
- Opção "apenas mídia" para economizar espaço
- Filtros combináveis e configuráveis

### Gestão de Rotas
- Múltiplas rotas de backup simultâneas
- Identificação por ID ou @username
- Destino flexível (Saved Messages ou chats específicos)

### Estado Persistente
- Evita duplicação de mensagens
- Controle de últimas mensagens processadas
- Arquivo JSON para configurações

## 🎨 Interface Visual

### Design System
- **Cores**: Paleta sage (verde acinzentado) e charcoal (cinza escuro)
- **Tipografia**: Inter para texto, JetBrains Mono para código
- **Componentes**: Cards, botões gradientes, indicadores de status
- **Animações**: Transições suaves e efeitos hover

### Responsividade
- Design adaptativo para todos os dispositivos
- Interface otimizada para desktop e mobile
- Navegação intuitiva e acessível

## 🔧 Configuração Avançada

### Arquivo de Configuração

```json
{
  "routes": {
    "@meu_canal": "me",
    "123456789": "backup_group_id"
  },
  "filters": {
    "media_only": false,
    "photos": true,
    "videos": true
  }
}
```

### Variáveis de Ambiente

```env
# Telegram API
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
SESSION_NAME=backup_session

# Configurações opcionais
LOG_LEVEL=INFO
MAX_WORKERS=4
REFRESH_INTERVAL=30
```

## 📊 Dashboard e Métricas

### Métricas Disponíveis
- **Rotas Ativas**: Número de rotas configuradas e funcionando
- **Mensagens Processadas**: Total acumulado de mensagens backupadas
- **Filtros Ativos**: Quantidade de filtros de conteúdo aplicados
- **Status do Sistema**: Online/Offline com indicadores visuais

### Visualizações
- Gráficos de barras para rotas e filtros
- Indicadores de status com cores intuitivas
- Tabelas interativas para gerenciamento
- Cards informativos com animações

## 🛡️ Segurança e Privacidade

### Segurança
- Credenciais armazenadas em arquivo .env
- Sessões criptografadas pelo Telethon
- Sem armazenamento de mensagens localmente

### Privacidade
- Apenas metadados são armazenados
- Mensagens são encaminhadas, não copiadas
- Respeito às configurações de privacidade do Telegram

## 🐛 Solução de Problemas

### Problemas Comuns

1. **Erro de Conexão**
   ```bash
   # Verificar conexão com internet
   ping google.com
   
   # Verificar credenciais
   cat config.env
   ```

2. **Sessão Expirada**
   ```bash
   # Remover arquivo de sessão
   rm *.session
   
   # Autenticar novamente
   streamlit run streamlit_app.py
   ```

3. **Erro de Permissão**
   - Verificar se o usuário pode enviar mensagens no destino
- Confirmar permissões no chat de destino

## 🤝 Contribuindo

### Como Contribuir
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Desenvolvimento
```bash
# Instalar dependências de desenvolvimento
uv pip install -e ".[dev]"

# Executar testes
pytest

# Formatar código
black .

# Verificar tipos
mypy .
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Telethon](https://github.com/LonamiWebs/Telethon) pela excelente biblioteca
- [Streamlit](https://streamlit.io/) pelo framework web incrível
- [UV](https://github.com/astral-sh/uv) pelo gerenciador de pacotes moderno
- Comunidade Python por ferramentas e bibliotecas fantásticas

## 📞 Suporte

- 📧 Email: dev@telegram-backup.com
- 🐛 Issues: [GitHub Issues](https://github.com/telegram-backup/telegram-backup-manager/issues)
- 📖 Wiki: [Documentação](https://github.com/telegram-backup/telegram-backup-manager/wiki)
- 💬 Discord: [Comunidade Telegram Backup](https://discord.gg/telegram-backup)

---

<div align="center">
    <strong>🚀 Telegram Backup Manager v2.0</strong><br>
    Sistema profissional de backup para Telegram com interface web moderna
</div>