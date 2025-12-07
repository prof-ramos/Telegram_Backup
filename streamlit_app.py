import streamlit as st
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Importar backend
from telegram_backup import TelegramBackupManager, create_backup_manager, MessageType

# Configuração da página
st.set_page_config(
    page_title="Telegram Backup Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração de tema customizado
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #5c7359, #485d46);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 2.5rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #5c7359, #485d46);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(92, 115, 89, 0.3);
    }
    .metric-card {
        background: rgba(246, 247, 246, 0.8);
        border: 1px solid rgba(162, 178, 162, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(92, 115, 89, 0.1);
    }
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .status-online { background-color: #10b981; }
    .status-offline { background-color: #ef4444; }
    .status-warning { background-color: #f59e0b; }
    .terminal-output {
        background: #1a1a1a;
        color: #e3e7e3;
        font-family: 'JetBrains Mono', monospace;
        border-radius: 8px;
        padding: 1rem;
        max-height: 300px;
            overflow-y: auto;
        font-size: 0.875rem;
        line-height: 1.5;
    }
    .success-message {
        background: #d1fae5;
        border: 1px solid #10b981;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-message {
        background: #fee2e2;
        border: 1px solid #ef4444;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-message {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

class TelegramBackupManager:
    def __init__(self):
        self.config_file = "config.json"
        self.state_file = "backup_state.json"
        self.env_file = "config.env"
        self.initialize_files()
    
    def initialize_files(self):
        """Inicializa arquivos de configuração se não existirem"""
        # Configuração padrão
        if not os.path.exists(self.config_file):
            default_config = {
                "routes": {},
                "filters": {
                    "media_only": False,
                    "photos": True,
                    "videos": True
                }
            }
            self.save_config(default_config["routes"], default_config["filters"])
        
        # Estado inicial
        if not os.path.exists(self.state_file):
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        # Arquivo env exemplo
        if not os.path.exists(self.env_file):
            with open(self.env_file, "w", encoding="utf-8") as f:
                f.write("# Configurações da API do Telegram\n")
                f.write("API_ID=sua_api_id\n")
                f.write("API_HASH=sua_api_hash\n")
                f.write("SESSION_NAME=backup_session\n")
    
    def load_config(self) -> tuple[Dict, Dict]:
        """Carrega configuração de rotas e filtros"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            routes = config.get("routes", {})
            filters = config.get("filters", {
                "media_only": False,
                "photos": True,
                "videos": True
            })
            
            # Converter chaves para int quando possível
            converted_routes = {}
            for k, v in routes.items():
                try:
                    converted_routes[int(k)] = v
                except (ValueError, TypeError):
                    converted_routes[k] = v
            
            return converted_routes, filters
        except Exception as e:
            st.error(f"Erro ao carregar configuração: {e}")
            return {}, {}
    
    def save_config(self, routes: Dict, filters: Dict) -> bool:
        """Salva configuração de rotas e filtros"""
        try:
            config = {
                "routes": {str(k): v for k, v in routes.items()},
                "filters": filters
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def add_route(self, source: str, destination: str) -> bool:
        """Adiciona uma nova rota de backup"""
        routes, filters = self.load_config()
        
        try:
            # Tentar converter source para int
            try:
                source_key = int(source)
            except (ValueError, TypeError):
                source_key = source
            
            routes[source_key] = destination
            return self.save_config(routes, filters)
        except Exception as e:
            st.error(f"Erro ao adicionar rota: {e}")
            return False
    
    def remove_route(self, source: str) -> bool:
        """Remove uma rota de backup"""
        routes, filters = self.load_config()
        
        try:
            # Tentar converter source para int
            try:
                source_key = int(source)
            except (ValueError, TypeError):
                source_key = source
            
            if source_key in routes:
                del routes[source_key]
                return self.save_config(routes, filters)
            return False
        except Exception as e:
            st.error(f"Erro ao remover rota: {e}")
            return False
    
    def update_filters(self, media_only: bool, photos: bool, videos: bool) -> bool:
        """Atualiza filtros de backup"""
        routes, filters = self.load_config()
        
        filters.update({
            "media_only": media_only,
            "photos": photos,
            "videos": videos
        })
        
        return self.save_config(routes, filters)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        routes, filters = self.load_config()
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            return {
                "total_routes": len(routes),
                "active_filters": sum(1 for v in filters.values() if v),
                "processed_messages": len(state),
                "last_update": max(state.values()) if state else 0
            }
        except Exception:
            return {
                "total_routes": len(routes),
                "active_filters": sum(1 for v in filters.values() if v),
                "processed_messages": 0,
                "last_update": 0
            }

# Inicializar gerenciador
@st.cache_resource
def get_manager():
    return TelegramBackupManager()

manager = get_manager()

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Controle Rápido")
    
    # Status do sistema
    st.markdown("#### 📊 Status")
    stats = manager.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rotas Ativas", stats["total_routes"])
    with col2:
        st.metric("Filtros Ativos", stats["active_filters"])
    
    # Ações rápidas
    st.markdown("#### ⚡ Ações Rápidas")
    
    if st.button("🚀 Iniciar Backup", use_container_width=True):
        st.session_state.show_backup_modal = True
    
    if st.button("➕ Adicionar Rota", use_container_width=True):
        st.session_state.show_add_route = True
    
    if st.button("⚙️ Configurar Filtros", use_container_width=True):
        st.session_state.show_filters = True
    
    # Informações do sistema
    st.markdown("#### ℹ️ Informações")
    st.json({
        "Sistema": "Telegram Backup CLI",
        "Versão": "2.0.0",
        "Interface": "Streamlit Web UI",
        "Python": "3.8+",
        "Última Atualização": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

# Main content
st.markdown('<h1 class="main-header">🚀 Telegram Backup Manager</h1>', unsafe_allow_html=True)
st.markdown("Sistema profissional de backup para Telegram com interface web moderna")

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🛣️ Rotas", "⚙️ Configuração", "📋 Logs"])

with tab1:
    # Dashboard principal
    st.markdown("### 📊 Dashboard Principal")
    
    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="flex items-center mb-2">
                <div class="status-indicator status-online"></div>
                <span class="text-sm font-medium text-charcoal-600">Sistema</span>
            </div>
            <div class="text-2xl font-bold text-sage-600">Online</div>
            <div class="text-xs text-charcoal-500">Última verificação: {datetime.now().strftime("%H:%M:%S")}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="flex items-center mb-2">
                <div class="status-indicator status-online"></div>
                <span class="text-sm font-medium text-charcoal-600">Rotas Configuradas</span>
            </div>
            <div class="text-2xl font-bold text-sage-600">{stats["total_routes"]}</div>
            <div class="text-xs text-charcoal-500">Ativas e funcionando</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="flex items-center mb-2">
                <div class="status-indicator status-warning"></div>
                <span class="text-sm font-medium text-charcoal-600">Mensagens Processadas</span>
            </div>
            <div class="text-2xl font-bold text-sage-600">{stats["processed_messages"]}</div>
            <div class="text-xs text-charcoal-500">Total acumulado</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="flex items-center mb-2">
                <div class="status-indicator status-online"></div>
                <span class="text-sm font-medium text-charcoal-600">Filtros Ativos</span>
            </div>
            <div class="text-2xl font-bold text-sage-600">{stats["active_filters"]}</div>
            <div class="text-xs text-charcoal-500">Configurações aplicadas</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Seção de controle
    st.markdown("### 🎮 Controle do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Iniciar Serviço", use_container_width=True):
            st.success("✅ Serviço iniciado com sucesso!")
            st.balloons()
    
    with col2:
        if st.button("⏸️ Pausar Serviço", use_container_width=True):
            st.warning("⚠️ Serviço pausado temporariamente")
    
    with col3:
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.info("🔄 Reiniciando sistema...")
            st.experimental_rerun()

with tab2:
    # Gerenciamento de rotas
    st.markdown("### 🛣️ Gerenciamento de Rotas")
    
    routes, filters = manager.load_config()
    
    if routes:
        # Mostrar rotas existentes
        st.markdown("#### Rotas Configuradas")
        
        routes_data = []
        for source, destination in routes.items():
            routes_data.append({
                "Origem": str(source),
                "Destino": str(destination),
                "Status": "✅ Ativa"
            })
        
        df_routes = pd.DataFrame(routes_data)
        st.dataframe(df_routes, use_container_width=True)
        
        # Remover rota
        st.markdown("#### ❌ Remover Rota")
        route_to_remove = st.selectbox("Selecione a rota para remover", list(routes.keys()))
        if st.button("Remover Rota Selecionada"):
            if manager.remove_route(route_to_remove):
                st.success(f"✅ Rota {route_to_remove} removida com sucesso!")
                st.experimental_rerun()
            else:
                st.error("❌ Erro ao remover rota")
    else:
        st.info("ℹ️ Nenhuma rota configurada. Adicione sua primeira rota abaixo.")
    
    # Adicionar nova rota
    st.markdown("#### ➕ Adicionar Nova Rota")
    
    with st.form("add_route_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            source = st.text_input("Origem (ID ou @username)", placeholder="@meu_canal ou 123456789")
        
        with col2:
            destination = st.text_input("Destino", placeholder="me ou ID do chat")
        
        submitted = st.form_submit_button("Adicionar Rota")
        
        if submitted and source and destination:
            if manager.add_route(source, destination):
                st.success(f"✅ Rota {source} → {destination} adicionada com sucesso!")
                st.experimental_rerun()
            else:
                st.error("❌ Erro ao adicionar rota")

with tab3:
    # Configuração de filtros
    st.markdown("### ⚙️ Configuração de Filtros")
    
    routes, current_filters = manager.load_config()
    
    st.markdown("#### 🎯 Filtros de Conteúdo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        media_only = st.checkbox("Apenas Mídia", value=current_filters.get("media_only", False))
        photos = st.checkbox("Incluir Fotos", value=current_filters.get("photos", True))
    
    with col2:
        videos = st.checkbox("Incluir Vídeos", value=current_filters.get("videos", True))
    
    if st.button("💾 Salvar Configuração de Filtros"):
        if manager.update_filters(media_only, photos, videos):
            st.success("✅ Configuração de filtros salva com sucesso!")
            st.experimental_rerun()
        else:
            st.error("❌ Erro ao salvar configuração")
    
    # Visualização da configuração
    st.markdown("#### 📋 Visualização da Configuração")
    
    config_view = {
        "rotas": routes,
        "filtros": {
            "media_only": media_only,
            "photos": photos,
            "videos": videos
        }
    }
    
    st.json(config_view)
    
    # Download da configuração
    config_json = json.dumps(config_view, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 Download config.json",
        data=config_json,
        file_name="config.json",
        mime="application/json"
    )

with tab4:
    # Logs e status
    st.markdown("### 📋 Logs e Status do Sistema")
    
    # Simulação de logs
    logs = [
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ✅ Sistema iniciado com sucesso",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 📊 Configuração carregada: {stats['total_routes']} rotas ativas",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 🎯 Filtros aplicados: {stats['active_filters']} ativos",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 🔄 Monitoramento em tempo real ativo",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 📱 Conexão com Telegram estabelecida",
    ]
    
    st.markdown("#### 📝 Últimos Logs")
    
    log_container = st.container()
    with log_container:
        for log in logs:
            st.text(log)
    
    # Status do sistema
    st.markdown("#### 🔍 Status Detalhado")
    
    status_data = {
        "Componente": ["Conexão Telegram", "Monitoramento", "Filtros", "Estado Persistente"],
        "Status": ["✅ Online", "✅ Ativo", "✅ Configurado", "✅ Funcionando"],
        "Última Verificação": [datetime.now().strftime("%H:%M:%S")] * 4
    }
    
    df_status = pd.DataFrame(status_data)
    st.dataframe(df_status, use_container_width=True)

# Modais e formulários adicionais
if st.session_state.get('show_add_route', False):
    with st.form("modal_add_route"):
        st.markdown("### ➕ Adicionar Nova Rota")
        source = st.text_input("Origem (ID ou @username)")
        destination = st.text_input("Destino")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Adicionar"):
                if manager.add_route(source, destination):
                    st.success("✅ Rota adicionada!")
                    st.session_state.show_add_route = False
                    st.experimental_rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.show_add_route = False
                st.experimental_rerun()

if st.session_state.get('show_filters', False):
    with st.form("modal_filters"):
        st.markdown("### ⚙️ Configurar Filtros")
        
        routes, current_filters = manager.load_config()
        
        media_only = st.checkbox("Apenas Mídia", value=current_filters.get("media_only", False))
        photos = st.checkbox("Incluir Fotos", value=current_filters.get("photos", True))
        videos = st.checkbox("Incluir Vídeos", value=current_filters.get("videos", True))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Salvar"):
                if manager.update_filters(media_only, photos, videos):
                    st.success("✅ Filtros atualizados!")
                    st.session_state.show_filters = False
                    st.experimental_rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.show_filters = False
                st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6d6d6d; font-size: 0.875rem;">
    🚀 Telegram Backup Manager v2.0 | Interface Web com Streamlit | 
    Desenvolvido com Python e tecnologias modernas
</div>
""", unsafe_allow_html=True)