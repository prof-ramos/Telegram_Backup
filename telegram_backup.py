"""
Telegram Backup Manager - Backend Core
Sistema profissional de backup para Telegram com interface web e CLI
"""

import asyncio
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import Message
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError, RPCError

# Importar modelos e banco de dados
from models import BackupConfig, BackupStats
from database import DatabaseManager

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

class TelegramBackupManager:
    """Gerenciador principal do sistema de backup"""
    
    def __init__(self, api_id: int = None, api_hash: str = None, session_name: str = None):
        self.api_id = api_id or int(os.getenv("API_ID", "0"))
        self.api_hash = api_hash or os.getenv("API_HASH", "")
        self.session_name = session_name or os.getenv("SESSION_NAME", "backup_session")
        
        if not self.api_id or not self.api_hash:
            raise ValueError("API_ID e API_HASH são obrigatórios")
        
        self.client = None
        self.db = DatabaseManager()
        self.config = self.db.load_config()
        self.stats = BackupStats()
        self.active_routes = {}
        self.is_running = False

        # Ensure directories exist
        Path("logs").mkdir(exist_ok=True)
        Path("backups").mkdir(exist_ok=True)

    def reload_config(self):
        """Reload configuration from DB"""
        self.config = self.db.load_config()

    def add_route(self, source: str, destination: str) -> bool:
        """Adiciona uma nova rota de backup"""
        try:
            self.db.save_route(str(source), str(destination))
            self.reload_config()
            logger.info(f"Rota adicionada: {source} → {destination}")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar rota: {e}")
            return False

    def remove_route(self, source: str) -> bool:
        """Remove uma rota de backup"""
        try:
            self.db.remove_route(str(source))
            self.reload_config()
            logger.info(f"Rota removida: {source}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover rota: {e}")
            return False

    def update_filters(self, **filters) -> bool:
        """Atualiza filtros de backup"""
        try:
            self.db.update_filters(filters)
            self.reload_config()
            logger.info(f"Filtros atualizados: {filters}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar filtros: {e}")
            return False

    def get_stats(self) -> BackupStats:
        """Retorna estatísticas atualizadas"""
        try:
            state = self.db.get_state()
            self.stats.processed_messages = len(state) # Number of tracked chats
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
            if message.action:
                return False
            
            filters = self.config.filters

            # Se não há filtros ativos (ou todos falsos que bloqueariam tudo?),
            # assumimos padrão de backup se a lógica anterior era "not any -> true".
            # No entanto, com Pydantic defaults, temos valores booleanos definidos.
            # Vamos seguir a lógica: se media_only é true, e não tem media, retorna false.
            
            if filters.media_only and not message.media:
                return False
            
            if message.media:
                if hasattr(message, 'photo') and filters.photos:
                    return True
                if hasattr(message, 'video') and filters.videos:
                    return True
                if hasattr(message, 'document') and filters.documents:
                    return True
                # Se tem media mas nenhum filtro específico ativo, retorna False?
                # A lógica original era: se media, verifica tipos.
                return False
            
            return filters.text_messages
        
        except Exception as e:
            logger.error(f"Erro ao verificar mensagem: {e}")
            return False

    async def connect(self) -> bool:
        """Conecta ao Telegram"""
        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                logger.error("Usuário não autorizado. Execute a autenticação primeiro via CLI ou script local.")
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
            
            if str(entity_id).lower() in ["me", "self", "saved"]:
                return "me"
            
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
            state = self.db.get_state()
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
                        self.db.update_state(source_id, message.id)
                        count += 1
                        
                        # Respeitar rate limit
                        if self.config.settings.rate_limit.enabled:
                             await asyncio.sleep(1.0 / self.config.settings.rate_limit.messages_per_second)
                    
                    except FloodWaitError as e:
                        logger.warning(f"FloodWait detectado. Aguardando {e.seconds} segundos.")
                        await asyncio.sleep(e.seconds)
                    except RPCError as e:
                        logger.error(f"Erro RPC do Telegram na mensagem {message.id}: {e}")
                        self.stats.errors_count += 1
                    except Exception as e:
                        logger.error(f"Erro inesperado ao encaminhar mensagem {message.id}: {e}")
                        self.stats.errors_count += 1
            
            logger.info(f"Backup histórico concluído: {count} mensagens de {source_id}")
            return count
        
        except Exception as e:
            logger.error(f"Erro no backup histórico: {e}")
            return 0

    async def start_real_time_backup(self):
        """Inicia backup em tempo real"""
        try:
            self.reload_config()
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
            
            logger.info("Iniciando backup histórico...")
            for source_entity, dest_entity in self.active_routes.items():
                await self.backup_historical_messages(source_entity, dest_entity)
            
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
                            
                            self.db.update_state(str(chat_id), message.id)
                            self.stats.processed_messages = self.db.get_total_processed_messages()
                            
                            logger.debug(f"Mensagem {message.id} backupada do chat {chat_id}")
                        
                        except FloodWaitError as e:
                            logger.warning(f"FloodWait detectado em tempo real. Aguardando {e.seconds} segundos.")
                            await asyncio.sleep(e.seconds)
                        except RPCError as e:
                            logger.error(f"Erro RPC em tempo real: {e}")
                            self.stats.errors_count += 1
                        except Exception as e:
                            logger.error(f"Erro inesperado em tempo real: {e}")
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
            
            me = await self.client.get_me()
            logger.info(f"Conectado como: {self.get_entity_display_name(me)}")
            
            if await self.start_real_time_backup():
                logger.info("Serviço iniciado. Aguardando mensagens...")
                await self.client.run_until_disconnected()
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao executar serviço: {e}")
            return False
        
        finally:
            await self.disconnect()
            self.is_running = False

def create_backup_manager() -> TelegramBackupManager:
    """Factory para criar instância do gerenciador"""
    api_id = int(os.getenv("API_ID", "0"))
    api_hash = os.getenv("API_HASH", "")
    return TelegramBackupManager(api_id=api_id, api_hash=api_hash)

async def run_async_backup():
    try:
        manager = create_backup_manager()
        await manager.run_backup_service()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")

def run_backup():
    asyncio.run(run_async_backup())

if __name__ == "__main__":
    run_backup()
