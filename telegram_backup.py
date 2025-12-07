"""
Telegram Backup Manager - Backend Core
Sistema profissional de backup para Telegram com interface web e CLI
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import aiofiles
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import Message, User, Chat, Channel
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Constantes
CONFIG_FILE = "config.json"
STATE_FILE = "backup_state.json"
SESSION_FILE = os.getenv("SESSION_NAME", "backup_session") + ".session"

class MessageType(Enum):
    """Tipos de mensagens para filtragem"""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    STICKER = "sticker"
    ANIMATION = "animation"

@dataclass
class BackupConfig:
    """Configuração do sistema de backup"""
    routes: Dict[str, str]
    filters: Dict[str, bool]
    settings: Dict[str, Any]
    
    @classmethod
    def default(cls) -> 'BackupConfig':
        return cls(
            routes={},
            filters={
                "media_only": False,
                "photos": True,
                "videos": True,
                "documents": False,
                "text_messages": True
            },
            settings={
                "max_workers": 4,
                "batch_size": 100,
                "retry_delay": 5,
                "timeout": 30,
                "rate_limit": {
                    "enabled": True,
                    "messages_per_second": 10
                }
            }
        )

@dataclass
class BackupStats:
    """Estatísticas do backup"""
    total_routes: int = 0
    active_routes: int = 0
    processed_messages: int = 0
    last_message_id: int = 0
    last_update: datetime = None
    errors_count: int = 0
    uptime_seconds: int = 0

class TelegramBackupManager:
    """Gerenciador principal do sistema de backup"""
    
    def __init__(self, api_id: int = None, api_hash: str = None, session_name: str = None):
        self.api_id = api_id or int(os.getenv("API_ID", "0"))
        self.api_hash = api_hash or os.getenv("API_HASH", "")
        self.session_name = session_name or os.getenv("SESSION_NAME", "backup_session")
        
        if not self.api_id or not self.api_hash:
            raise ValueError("API_ID e API_HASH são obrigatórios")
        
        self.client = None
        self.config = BackupConfig.default()
        self.stats = BackupStats()
        self.active_routes = {}
        self.is_running = False
        self._setup_files()
    
    def _setup_files(self):
        """Configura arquivos necessários"""
        # Criar diretórios
        Path("logs").mkdir(exist_ok=True)
        Path("backups").mkdir(exist_ok=True)
        
        # Carregar configuração existente
        self.load_config()
        self.load_state()
    
    def load_config(self) -> bool:
        """Carrega configuração do arquivo JSON"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.config.routes = data.get("routes", {})
                self.config.filters.update(data.get("filters", {}))
                self.config.settings.update(data.get("settings", {}))
                
                logger.info(f"Configuração carregada: {len(self.config.routes)} rotas")
                return True
            else:
                logger.warning("Arquivo de configuração não encontrado, usando padrões")
                self.save_config()
                return False
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return False
    
    def save_config(self) -> bool:
        """Salva configuração no arquivo JSON"""
        try:
            config_data = {
                "routes": self.config.routes,
                "filters": self.config.filters,
                "settings": self.config.settings
            }
            
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info("Configuração salva com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def load_state(self) -> Dict[str, int]:
        """Carrega estado de processamento"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return {}
    
    def save_state(self, state: Dict[str, int]) -> bool:
        """Salva estado de processamento"""
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
            return False
    
    def add_route(self, source: str, destination: str) -> bool:
        """Adiciona uma nova rota de backup"""
        try:
            # Converter source para int se possível
            try:
                source_key = int(source)
            except (ValueError, TypeError):
                source_key = source
            
            self.config.routes[str(source_key)] = destination
            success = self.save_config()
            
            if success:
                logger.info(f"Rota adicionada: {source_key} → {destination}")
                self.stats.total_routes = len(self.config.routes)
            
            return success
        except Exception as e:
            logger.error(f"Erro ao adicionar rota: {e}")
            return False
    
    def remove_route(self, source: str) -> bool:
        """Remove uma rota de backup"""
        try:
            # Converter source para int se possível
            try:
                source_key = int(source)
            except (ValueError, TypeError):
                source_key = source
            
            source_str = str(source_key)
            
            if source_str in self.config.routes:
                del self.config.routes[source_str]
                success = self.save_config()
                
                if success:
                    logger.info(f"Rota removida: {source_key}")
                    self.stats.total_routes = len(self.config.routes)
                
                return success
            
            logger.warning(f"Rota não encontrada: {source_key}")
            return False
        except Exception as e:
            logger.error(f"Erro ao remover rota: {e}")
            return False
    
    def update_filters(self, **filters) -> bool:
        """Atualiza filtros de backup"""
        try:
            self.config.filters.update(filters)
            success = self.save_config()
            
            if success:
                logger.info(f"Filtros atualizados: {filters}")
            
            return success
        except Exception as e:
            logger.error(f"Erro ao atualizar filtros: {e}")
            return False
    
    def get_stats(self) -> BackupStats:
        """Retorna estatísticas atualizadas"""
        try:
            state = self.load_state()
            self.stats.processed_messages = len(state)
            self.stats.total_routes = len(self.config.routes)
            self.stats.active_routes = len(self.active_routes)
            self.stats.last_update = datetime.now()
            
            if state:
                self.stats.last_message_id = max(state.values())
            
            return self.stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return self.stats
    
    def should_backup_message(self, message: Message) -> bool:
        """Verifica se uma mensagem deve ser backupada"""
        try:
            # Ignorar mensagens de serviço
            if message.action:
                return False
            
            # Se não há filtros ativos, backupar tudo
            if not any(self.config.filters.values()):
                return True
            
            # Verificar filtros de mídia
            if self.config.filters.get("media_only", False) and not message.media:
                return False
            
            # Verificar tipo específico de mídia
            if message.media:
                if hasattr(message, 'photo') and self.config.filters.get("photos", True):
                    return True
                if hasattr(message, 'video') and self.config.filters.get("videos", True):
                    return True
                if hasattr(message, 'document') and self.config.filters.get("documents", False):
                    return True
                return False
            
            # Backupar mensagens de texto se permitido
            return self.config.filters.get("text_messages", True)
        
        except Exception as e:
            logger.error(f"Erro ao verificar mensagem: {e}")
            return False
    
    async def connect(self) -> bool:
        """Conecta ao Telegram"""
        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                logger.error("Usuário não autorizado. Execute a autenticação primeiro.")
                return False
            
            logger.info("Conectado ao Telegram com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao Telegram: {e}")
            return False
    
    async def disconnect(self):
        """Desconecta do Telegram"""
        if self.client:
            await self.client.disconnect()
            logger.info("Desconectado do Telegram")
    
    async def resolve_entity(self, entity_id: str):
        """Resolve uma entidade do Telegram"""
        try:
            if not self.client:
                await self.connect()
            
            # Tratar casos especiais
            if entity_id.lower() in ["me", "self", "saved"]:
                return "me"
            
            # Tentar converter para int
            try:
                entity_id = int(entity_id)
            except (ValueError, TypeError):
                pass
            
            entity = await self.client.get_entity(entity_id)
            return entity
        except Exception as e:
            logger.error(f"Erro ao resolver entidade {entity_id}: {e}")
            return None
    
    def get_entity_display_name(self, entity) -> str:
        """Obtém nome amigável de uma entidade"""
        try:
            if hasattr(entity, "title") and entity.title:
                return entity.title
            
            if hasattr(entity, "first_name") or hasattr(entity, "last_name"):
                first_name = getattr(entity, "first_name", "") or ""
                last_name = getattr(entity, "last_name", "") or ""
                if first_name or last_name:
                    return f"{first_name} {last_name}".strip()
            
            if hasattr(entity, "username") and entity.username:
                return f"@{entity.username}"
            
            return str(getattr(entity, "id", "desconhecido"))
        except Exception:
            return "entidade_desconhecida"
    
    async def backup_historical_messages(self, source_entity, destination_entity) -> int:
        """Faz backup de mensagens históricas de um chat"""
        try:
            state = self.load_state()
            source_id = str(source_entity.id)
            last_id = state.get(source_id, 0)
            
            logger.info(f"Iniciando backup histórico de {source_id} (último ID: {last_id})")
            
            count = 0
            async for message in self.client.iter_messages(
                source_entity, 
                min_id=last_id, 
                reverse=True
            ):
                if self.should_backup_message(message):
                    try:
                        await self.client.forward_messages(destination_entity, message)
                        state[source_id] = message.id
                        count += 1
                        
                        # Salvar estado a cada 50 mensagens
                        if count % 50 == 0:
                            self.save_state(state)
                        
                        # Respeitar rate limit
                        if self.config.settings.get("rate_limit", {}).get("enabled", False):
                            await asyncio.sleep(1 / self.config.settings["rate_limit"]["messages_per_second"])
                    
                    except Exception as e:
                        logger.error(f"Erro ao encaminhar mensagem {message.id}: {e}")
                        self.stats.errors_count += 1
            
            self.save_state(state)
            logger.info(f"Backup histórico concluído: {count} mensagens de {source_id}")
            
            return count
        
        except Exception as e:
            logger.error(f"Erro no backup histórico: {e}")
            return 0
    
    async def start_real_time_backup(self):
        """Inicia backup em tempo real"""
        try:
            # Resolver todas as rotas
            self.active_routes = {}
            
            for source, destination in self.config.routes.items():
                source_entity = await self.resolve_entity(source)
                dest_entity = await self.resolve_entity(destination)
                
                if source_entity and dest_entity:
                    self.active_routes[source_entity.id] = dest_entity
                    logger.info(f"Rota ativa: {self.get_entity_display_name(source_entity)} → {self.get_entity_display_name(dest_entity)}")
            
            if not self.active_routes:
                logger.warning("Nenhuma rota válida encontrada")
                return False
            
            # Fazer backup histórico primeiro
            logger.info("Iniciando backup histórico...")
            for source_entity, dest_entity in self.active_routes.items():
                await self.backup_historical_messages(source_entity, dest_entity)
            
            # Configurar handler para mensagens novas
            @self.client.on(events.NewMessage)
            async def handle_new_message(event):
                chat_id = event.chat_id
                
                if chat_id in self.active_routes:
                    message = event.message
                    
                    if self.should_backup_message(message):
                        try:
                            await self.client.forward_messages(
                                self.active_routes[chat_id], 
                                message
                            )
                            
                            # Atualizar estado
                            state = self.load_state()
                            state[str(chat_id)] = message.id
                            self.save_state(state)
                            
                            self.stats.processed_messages += 1
                            logger.debug(f"Mensagem {message.id} backupada do chat {chat_id}")
                        
                        except Exception as e:
                            logger.error(f"Erro ao backupar mensagem em tempo real: {e}")
                            self.stats.errors_count += 1
            
            self.is_running = True
            logger.info("Backup em tempo real iniciado com sucesso")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao iniciar backup em tempo real: {e}")
            return False
    
    async def run_backup_service(self):
        """Executa o serviço completo de backup"""
        try:
            if not await self.connect():
                return False
            
            # Obter informações do usuário
            me = await self.client.get_me()
            logger.info(f"Conectado como: {self.get_entity_display_name(me)}")
            
            # Iniciar backup
            if await self.start_real_time_backup():
                logger.info("Serviço iniciado. Aguardando mensagens...")
                
                # Manter o serviço rodando
                try:
                    await self.client.run_until_disconnected()
                except KeyboardInterrupt:
                    logger.info("Serviço interrompido pelo usuário")
                except Exception as e:
                    logger.error(f"Erro no serviço: {e}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao executar serviço: {e}")
            return False
        
        finally:
            await self.disconnect()
            self.is_running = False

# Funções auxiliares para CLI e Interface Web
def create_backup_manager() -> TelegramBackupManager:
    """Factory para criar instância do gerenciador"""
    api_id = int(os.getenv("API_ID", "0"))
    api_hash = os.getenv("API_HASH", "")
    
    if not api_id or not api_hash:
        raise ValueError("API_ID e API_HASH devem estar configurados no config.env")
    
    return TelegramBackupManager(api_id=api_id, api_hash=api_hash)

async def run_async_backup():
    """Função auxiliar para executar backup assíncrono"""
    try:
        manager = create_backup_manager()
        await manager.run_backup_service()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")

def run_backup():
    """Função síncrona para executar backup"""
    asyncio.run(run_async_backup())

if __name__ == "__main__":
    run_backup()