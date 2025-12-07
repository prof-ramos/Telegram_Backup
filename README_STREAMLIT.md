# 🚀 Telegram Backup Manager v2.0 - Interface Streamlit

Interface web moderna e intuitiva para o sistema de backup do Telegram, desenvolvida com Streamlit e tecnologias modernas.

## ✨ Novidades

- 🌐 **Interface Web Moderna**: Design responsivo e intuitivo
- 📊 **Dashboard Interativo**: Métricas em tempo real
- 🎨 **Design Aprimorado**: Cores, animações e UX melhorada
- ⚡ **Performance Otimizada**: Carregamento rápido e operações assíncronas
- 📱 **Mobile Friendly**: Interface adaptativa para todos dispositivos

## 🛠️ Tecnologias

- **Streamlit**: Framework web para aplicações Python
- **Telethon**: Biblioteca para automação do Telegram
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas
- **Tailwind CSS**: Estilização moderna (via componentes customizados)

## 📦 Instalação

### Método 1: Script de Instalação Automatizada

```bash
# Baixar e executar o instalador
curl -LsSf https://astral.sh/uv/install.sh | sh
bash install.sh
```

### Método 2: Instalação Manual

```bash
# Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Criar ambiente virtual
uv venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
uv pip install -r requirements.txt
```

### Método 3: Usando pip tradicional

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

## 🚀 Como Usar

### 1. Configurar Credenciais

Crie o arquivo `config.env` com suas credenciais do Telegram:

```env
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
SESSION_NAME=backup_session
```

> **⚠️ Importante**: Obtenha suas credenciais em [my.telegram.org](https://my.telegram.org)

### 2. Executar a Aplicação

```bash
# Método 1: Script de execução
bash run.sh

# Método 2: Diretamente com Streamlit
streamlit run streamlit_app.py

# Método 3: Com configurações customizadas
streamlit run streamlit_app.py --server.port=8501 --server.address=localhost
```

### 3. Acessar a Interface

A aplicação abrirá automaticamente no navegador em: **http://localhost:8501**

## 📱 Interface Web

### Dashboard Principal

O dashboard principal oferece:

- **📊 Métricas em Tempo Real**: Visualize status do sistema
- **🎮 Controle Rápido**: Inicie, pause ou reinicie o serviço
- **📈 Estatísticas**: Acompanhe mensagens processadas e rotas ativas
- **🔍 Status do Sistema**: Indicadores visuais de conexão

### Gerenciamento de Rotas

- **📋 Visualização em Tabela**: Todas as rotas configuradas
- **➕ Adicionar Rotas**: Interface formulário intuitiva
- **❌ Remover Rotas**: Seleção visual para exclusão
- **✅ Status das Rotas**: Indicadores de atividade

### Configuração de Filtros

- **🎯 Filtros Visuais**: Checkboxes para fácil configuração
- **📊 Visualização JSON**: Formato legível da configuração
- **💾 Download de Config**: Exporte suas configurações
- **⚙️ Opções Avançadas**: Configurações adicionais

### Monitoramento

- **📋 Logs em Tempo Real**: Acompanhe operações do sistema
- **🔍 Status Detalhado**: Verifique saúde dos componentes
- **📊 Dashboard Interativo**: Gráficos e visualizações
- **⚡ Atualização Automática**: Interface se atualiza automaticamente

## 🎨 Design System

### Cores

- **Sage**: Verde acinzentado (#5c7359) - Cor principal
- **Charcoal**: Cinza escuro (#3d3d3d) - Texto e detalhes
- **Background**: Fundo claro (#f6f7f6) - Interface limpa
- **Accent**: Azul suave (#3b82f6) - Ações e links

### Tipografia

- **Inter**: Fonte principal para textos
- **JetBrains Mono**: Fonte monoespaçada para código
- **Tamanhos**: Hierarquia clara de títulos e textos

### Componentes

- **Cards**: Com sombra e bordas arredondadas
- **Botões**: Gradientes e efeitos hover
- **Indicadores**: Status coloridos e animados
- **Formulários**: Campos estilizados e validação

## ⚙️ Configuração

### Arquivo de Configuração

O sistema usa `config.json` para armazenar configurações:

```json
{
  "routes": {
    "@meu_canal": "me",
    "123456789": "backup_group_id"
  },
  "filters": {
    "media_only": false,
    "photos": true,
    "videos": true,
    "documents": false,
    "text_messages": true
  }
}
```

### Variáveis de Ambiente

Configure no arquivo `config.env`:

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

## 🔧 Funcionalidades Técnicas

### Backend Robustos

- **Telethon**: Conexão segura com API do Telegram
- **Async/Await**: Operações não-bloqueantes
- **Rate Limiting**: Controle de taxa de requisições
- **Error Handling**: Tratamento robusto de erros

### Frontend Moderno

- **Streamlit Components**: Componentes customizados
- **Real-time Updates**: Atualização automática de dados
- **Responsive Design**: Adaptação a diferentes tamanhos de tela
- **Progressive Enhancement**: Funcionalidade básica sempre disponível

### Armazenamento

- **JSON**: Configurações e estado em formato JSON
- **File-based**: Armazenamento local simples
- **Backup Automático**: Salvamento periódico de estado
- **Export/Import**: Capacidade de migrar configurações

## 📊 Métricas e Monitoramento

### Estatísticas Disponíveis

- **Rotas Ativas**: Número de rotas configuradas
- **Mensagens Processadas**: Total acumulado de mensagens
- **Taxa de Sucesso**: Percentual de operações bem-sucedidas
- **Tempo de Atividade**: Horas de funcionamento contínuo
- **Erros**: Contador de erros e falhas

### Visualizações

- **Gráficos de Barras**: Distribuição de tipos de mensagem
- **Indicadores de Status**: Cores para diferentes estados
- **Tabelas Interativas**: Dados organizados e filtráveis
- **Cards Informativos**: Resumos visuais de métricas

## 🛡️ Segurança

### Proteção de Dados

- **Credenciais Seguras**: Armazenadas em arquivo .env
- **Sessões Criptografadas**: Proteção pelo Telethon
- **Sem Armazenamento Local**: Mensagens não são salvas localmente
- **Privacidade**: Respeito às configurações do Telegram

### Boas Práticas

- **Nunca compartilhe credenciais**
- **Use senhas fortes para sessões**
- **Mantenha o sistema atualizado**
- **Monitore logs regularmente**

## 🐛 Solução de Problemas

### Erros Comuns

1. **"Module not found"**
   ```bash
   # Reinstalar dependências
   pip install -r requirements.txt
   ```

2. **"API_ID não configurado"**
   ```bash
   # Verificar config.env
   cat config.env
   ```

3. **"Conexão falhou"**
   ```bash
   # Verificar internet e credenciais
   ping google.com
   ```

4. **"Streamlit não inicia"**
   ```bash
   # Verificar porta
   netstat -an | grep 8501
   ```

### Logs e Debugging

- **Logs do Sistema**: `telegram_backup.log`
- **Logs do Streamlit**: Console do terminal
- **Configuração Verbose**: `LOG_LEVEL=DEBUG`

## 🚀 Performance

### Otimizações

- **Cache Inteligente**: Dados frequentes em cache
- **Lazy Loading**: Carregamento sob demanda
- **Async Operations**: Operações não-bloqueantes
- **Memory Management**: Gerenciamento eficiente de memória

### Requisitos Mínimos

- **Python**: 3.8 ou superior
- **RAM**: 512MB livre
- **Disco**: 100MB para instalação
- **Internet**: Conexão estável para Telegram

## 🤝 Contribuindo

### Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Desenvolva sua contribuição
4. Teste completamente
5. Abra um Pull Request

### Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install pytest black flake8 mypy

# Executar testes
python test_system.py

# Formatar código
black .

# Verificar tipos
mypy .
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.

## 🙏 Agradecimentos

- [Streamlit](https://streamlit.io/) pelo framework incrível
- [Telethon](https://github.com/LonamiWebs/Telethon) pela biblioteca robusta
- [Tailwind CSS](https://tailwindcss.com/) pela inspiração de design
- Comunidade Python por ferramentas fantásticas

## 📞 Suporte

- **Documentação**: Este README e comentários no código
- **Issues**: Reporte problemas e sugira melhorias
- **Wiki**: Guias e tutoriais adicionais

---

<div align="center">
    <strong>🚀 Telegram Backup Manager v2.0 - Interface Streamlit</strong><br>
    Interface web moderna para gerenciamento de backup do Telegram
</div>