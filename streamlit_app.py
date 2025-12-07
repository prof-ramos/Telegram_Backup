import streamlit as st
import asyncio
import json
import os
import sys
import subprocess
import signal
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Importar backend
from telegram_backup import TelegramBackupManager, create_backup_manager
from models import BackupConfig, BackupStats

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

# Service Management Functions
SERVICE_PID_FILE = "service.pid"

def is_service_running() -> bool:
    if not os.path.exists(SERVICE_PID_FILE):
        return False
    try:
        with open(SERVICE_PID_FILE, "r") as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            # Stale PID file
            return False
    except (ValueError, FileNotFoundError):
        return False

def start_service():
    if is_service_running():
        st.warning("Service is already running.")
        return

    try:
        # Use sys.executable to ensure we use the same python interpreter
        subprocess.Popen([sys.executable, "backup_service.py"])
        st.success("Service started successfully!")
        time.sleep(1) # Wait for startup
        st.rerun()
    except Exception as e:
        st.error(f"Failed to start service: {e}")

def stop_service():
    if not is_service_running():
        st.warning("Service is not running.")
        return

    try:
        with open(SERVICE_PID_FILE, "r") as f:
            pid = int(f.read().strip())
        
        os.kill(pid, signal.SIGTERM)
        st.success("Stop signal sent to service.")
        time.sleep(1) # Wait for cleanup
        st.rerun()
    except Exception as e:
        st.error(f"Failed to stop service: {e}")

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
        st.metric("Rotas Ativas", stats.total_routes)
    with col2:
        st.metric("Filtros Ativos", stats.active_routes) # Using active routes as proxy or we can count active filters
    
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
    
    service_status = is_service_running()
    status_text = "Online" if service_status else "Offline"
    status_class = "status-online" if service_status else "status-offline"

    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="flex items-center mb-2">
                <div class="status-indicator {status_class}"></div>
                <span class="text-sm font-medium text-charcoal-600">Serviço de Backup</span>
            </div>
            <div class="text-2xl font-bold text-sage-600">{status_text}</div>
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
            <div class="text-2xl font-bold text-sage-600">{stats.total_routes}</div>
            <div class="text-xs text-charcoal-500">Ativas e funcionando</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="flex items-center mb-2">
                <div class="status-indicator status-warning"></div>
                <span class="text-sm font-medium text-charcoal-600">Chats Monitorados</span>
            </div>
            <div class="text-2xl font-bold text-sage-600">{stats.processed_messages}</div>
            <div class="text-xs text-charcoal-500">Total acumulado</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        # Count active filters
        filters_dict = manager.config.filters.dict()
        active_filters = sum(1 for v in filters_dict.values() if v)
        st.markdown(f'''
        <div class="metric-card">
            <div class="flex items-center mb-2">
                <div class="status-indicator status-online"></div>
                <span class="text-sm font-medium text-charcoal-600">Filtros Ativos</span>
            </div>
            <div class="text-2xl font-bold text-sage-600">{active_filters}</div>
            <div class="text-xs text-charcoal-500">Configurações aplicadas</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Seção de controle
    st.markdown("### 🎮 Controle do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Iniciar Serviço", use_container_width=True, disabled=service_status):
            start_service()
    
    with col2:
        if st.button("⏸️ Parar Serviço", use_container_width=True, disabled=not service_status):
            stop_service()
    
    with col3:
        if st.button("🔄 Atualizar UI", use_container_width=True):
            st.rerun()

with tab2:
    # Gerenciamento de rotas
    st.markdown("### 🛣️ Gerenciamento de Rotas")
    
    manager.reload_config()
    routes = manager.config.routes
    
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
                st.rerun()
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
                st.rerun()
            else:
                st.error("❌ Erro ao adicionar rota")

with tab3:
    # Configuração de filtros
    st.markdown("### ⚙️ Configuração de Filtros")
    
    manager.reload_config()
    current_filters = manager.config.filters
    
    st.markdown("#### 🎯 Filtros de Conteúdo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        media_only = st.checkbox("Apenas Mídia", value=current_filters.media_only)
        photos = st.checkbox("Incluir Fotos", value=current_filters.photos)
    
    with col2:
        videos = st.checkbox("Incluir Vídeos", value=current_filters.videos)
        documents = st.checkbox("Incluir Documentos", value=current_filters.documents)
    
    if st.button("💾 Salvar Configuração de Filtros"):
        if manager.update_filters(
            media_only=media_only,
            photos=photos,
            videos=videos,
            documents=documents
        ):
            st.success("✅ Configuração de filtros salva com sucesso!")
            st.rerun()
        else:
            st.error("❌ Erro ao salvar configuração")
    
    # Visualização da configuração
    st.markdown("#### 📋 Visualização da Configuração")
    
    config_view = {
        "rotas": routes,
        "filtros": current_filters.dict()
    }
    
    st.json(config_view)

with tab4:
    # Logs e status
    st.markdown("### 📋 Logs e Status do Sistema")
    
    st.markdown("#### 📝 Logs do Serviço")
    
    if os.path.exists("telegram_backup.log"):
        with open("telegram_backup.log", "r") as f:
            # Read last 20 lines
            lines = f.readlines()
            last_logs = lines[-20:]

        log_container = st.container()
        with log_container:
            for log in last_logs:
                st.text(log.strip())
    else:
        st.info("Nenhum arquivo de log encontrado.")
    
    # Status do sistema
    st.markdown("#### 🔍 Status Detalhado")
    
    status_data = {
        "Componente": ["Service Runner", "Conexão DB"],
        "Status": [
            "✅ Ativo" if service_status else "🔴 Parado",
            "✅ Conectado"
        ],
        "Última Verificação": [datetime.now().strftime("%H:%M:%S")] * 2
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
                    st.rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.show_add_route = False
                st.rerun()

if st.session_state.get('show_filters', False):
    with st.form("modal_filters"):
        st.markdown("### ⚙️ Configurar Filtros")
        
        manager.reload_config()
        current_filters = manager.config.filters
        
        media_only = st.checkbox("Apenas Mídia", value=current_filters.media_only)
        photos = st.checkbox("Incluir Fotos", value=current_filters.photos)
        videos = st.checkbox("Incluir Vídeos", value=current_filters.videos)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Salvar"):
                if manager.update_filters(media_only=media_only, photos=photos, videos=videos):
                    st.success("✅ Filtros atualizados!")
                    st.session_state.show_filters = False
                    st.rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.show_filters = False
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6d6d6d; font-size: 0.875rem;">
    🚀 Telegram Backup Manager v2.0 | Interface Web com Streamlit | 
    Desenvolvido com Python e tecnologias modernas
</div>
""", unsafe_allow_html=True)
