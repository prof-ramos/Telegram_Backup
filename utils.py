"""
Utilitários para o Telegram Backup Manager
Funções auxiliares para a interface Streamlit
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import streamlit as st
from telegram_backup import TelegramBackupManager, create_backup_manager

class StreamlitUtils:
    """Classe utilitária para funções da interface Streamlit"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formata tamanho de arquivo em bytes para formato legível"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Formata datetime para string legível"""
        if not dt:
            return "Nunca"
        
        # Garantir que dt tenha timezone (se for naive, assume UTC ou local de acordo com lógica do Telethon)
        # Telethon retorna aware datetimes (UTC). datetime.now() é naive por padrão.
        # Solução: converter tudo para UTC aware.

        from datetime import timezone

        now = datetime.now(timezone.utc)

        if dt.tzinfo is None:
            # Se dt é naive, assume UTC para comparação segura
            dt = dt.replace(tzinfo=timezone.utc)

        diff = now - dt
        
        if diff.total_seconds() < 60:
            return f"Há {int(diff.total_seconds())} segundos"
        elif diff.total_seconds() < 3600:
            return f"Há {int(diff.total_seconds() / 60)} minutos"
        elif diff.total_seconds() < 86400:
            return f"Há {int(diff.total_seconds() / 3600)} horas"
        else:
            return dt.strftime("%d/%m/%Y %H:%M")
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Retorna cor do status para indicadores visuais"""
        status_colors = {
            "online": "#10b981",      # Verde
            "offline": "#ef4444",     # Vermelho
            "warning": "#f59e0b",     # Amarelo
            "info": "#3b82f6",        # Azul
            "success": "#10b981",     # Verde
            "error": "#ef4444",       # Vermelho
            "pending": "#6b7280",     # Cinza
            "processing": "#8b5cf6"   # Roxo
        }
        return status_colors.get(status.lower(), "#6b7280")
    
    @staticmethod
    def create_route_card(source: str, destination: str, status: str = "ativa") -> Dict[str, Any]:
        """Cria card visual para uma rota de backup"""
        return {
            "source": source,
            "destination": destination,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "last_activity": None,
            "messages_count": 0
        }
    
    @staticmethod
    def load_example_chats() -> List[Dict[str, Any]]:
        """Carrega exemplos de chats para demonstração"""
        return [
            {
                "id": "@python_br",
                "name": "Python Brasil",
                "type": "Canal",
                "members": 50000,
                "description": "Comunidade Python do Brasil"
            },
            {
                "id": "123456789",
                "name": "Grupo Tech News",
                "type": "Grupo",
                "members": 1250,
                "description": "Notícias sobre tecnologia"
            },
            {
                "id": "@datascience_channel",
                "name": "Data Science Channel",
                "type": "Canal",
                "members": 8500,
                "description": "Conteúdo sobre ciência de dados"
            },
            {
                "id": "987654321",
                "name": "DevOps Community",
                "type": "Grupo",
                "members": 3400,
                "description": "Comunidade DevOps"
            }
        ]
    
    @staticmethod
    def create_backup_statistics() -> Dict[str, Any]:
        """Cria estatísticas de exemplo para demonstração"""
        return {
            "total_messages": 15420,
            "messages_today": 127,
            "messages_this_week": 892,
            "active_chats": 8,
            "total_storage": "2.3 GB",
            "uptime_hours": 168,
            "success_rate": 99.7,
            "errors_count": 45,
            "last_backup": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_log_messages(count: int = 10) -> List[str]:
        """Gera mensagens de log para demonstração"""
        logs = []
        base_time = datetime.now()
        
        messages = [
            "Sistema iniciado com sucesso",
            "Conectado ao Telegram",
            "Configuração carregada",
            "Rotas verificadas",
            "Backup iniciado",
            "Mensagem processada",
            "Estado salvo",
            "Conexão verificada",
            "Filtros aplicados",
            "Serviço rodando"
        ]
        
        for i in range(count):
            time_offset = i * 30  # 30 segundos entre logs
            log_time = base_time - timedelta(seconds=time_offset)
            message = messages[i % len(messages)]
            logs.append(f"{log_time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")
        
        return logs
    
    @staticmethod
    def validate_telegram_credentials(api_id: str, api_hash: str) -> bool:
        """Valida formato das credenciais do Telegram"""
        try:
            # Verificar se API_ID é numérico
            int(api_id)
            
            # Verificar se API_HASH tem formato válido (32 caracteres hex)
            if len(api_hash) != 32:
                return False
            
            # Verificar se é hexadecimal
            int(api_hash, 16)
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def create_config_template() -> Dict[str, Any]:
        """Cria template de configuração"""
        return {
            "routes": {
                "@meu_canal": "me",
                "123456789": "backup_group"
            },
            "filters": {
                "media_only": False,
                "photos": True,
                "videos": True,
                "documents": False,
                "text_messages": True
            },
            "settings": {
                "max_workers": 4,
                "batch_size": 100,
                "retry_delay": 5,
                "timeout": 30
            }
        }
    
    @staticmethod
    def export_configuration(manager: TelegramBackupManager, filename: str) -> bool:
        """Exporta configuração para arquivo"""
        try:
            config = {
                "routes": manager.config.routes,
                "filters": manager.config.filters,
                "settings": manager.config.settings,
                "export_date": datetime.now().isoformat(),
                "version": "2.0.0"
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Erro ao exportar configuração: {e}")
            return False
    
    @staticmethod
    def import_configuration(filename: str) -> Optional[Dict[str, Any]]:
        """Importa configuração de arquivo"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validar estrutura básica
            required_keys = ["routes", "filters"]
            if not all(key in config for key in required_keys):
                st.error("Arquivo de configuração inválido")
                return None
            
            return config
        except Exception as e:
            st.error(f"Erro ao importar configuração: {e}")
            return None

# Funções auxiliares para cache e performance
@st.cache_data(ttl=60)
def get_system_info():
    """Obtém informações do sistema (com cache)"""
    return {
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "platform": os.sys.platform,
        "current_time": datetime.now().isoformat(),
        "working_directory": os.getcwd()
    }

@st.cache_data(ttl=30)
def load_configuration_summary():
    """Carrega resumo da configuração (com cache)"""
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return {
                "routes_count": len(config.get("routes", {})),
                "filters_active": sum(1 for v in config.get("filters", {}).values() if v),
                "has_config": True
            }
        else:
            return {
                "routes_count": 0,
                "filters_active": 0,
                "has_config": False
            }
    except Exception:
        return {
            "routes_count": 0,
            "filters_active": 0,
            "has_config": False
        }

# Funções de utilidade para Streamlit
def show_success_message(message: str):
    """Mostra mensagem de sucesso com estilo"""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def show_error_message(message: str):
    """Mostra mensagem de erro com estilo"""
    st.markdown(f"""
    <div class="error-message">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)

def show_warning_message(message: str):
    """Mostra mensagem de aviso com estilo"""
    st.markdown(f"""
    <div class="warning-message">
        ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)

def show_info_message(message: str):
    """Mostra mensagem informativa com estilo"""
    st.info(f"ℹ️ {message}")

# Constantes úteis
MESSAGE_TYPES = {
    "text": "Mensagens de Texto",
    "photo": "Fotos",
    "video": "Vídeos", 
    "document": "Documentos",
    "audio": "Áudios",
    "sticker": "Stickers",
    "animation": "Animações"
}

STATUS_COLORS = {
    "online": "#10b981",
    "offline": "#ef4444", 
    "warning": "#f59e0b",
    "info": "#3b82f6",
    "success": "#10b981",
    "error": "#ef4444",
    "pending": "#6b7280",
    "processing": "#8b5cf6"
}

# Exportar classes e funções
__all__ = [
    'StreamlitUtils',
    'get_system_info',
    'load_configuration_summary',
    'show_success_message',
    'show_error_message', 
    'show_warning_message',
    'show_info_message',
    'MESSAGE_TYPES',
    'STATUS_COLORS'
]