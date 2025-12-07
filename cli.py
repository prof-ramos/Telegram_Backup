#!/usr/bin/env python3
"""
Telegram Backup CLI - Interface de Linha de Comando
Interface moderna com Rich para gerenciamento do sistema de backup
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn

# Importar backend
from telegram_backup import (
    TelegramBackupManager, 
    create_backup_manager, 
    run_backup
)
from models import MessageType

# Configuração
load_dotenv()
console = Console()

class RichTelegramCLI:
    """Interface CLI com Rich para gerenciamento do backup"""
    
    def __init__(self):
        self.manager = None
        self.setup_manager()
    
    def setup_manager(self):
        """Configura o gerenciador de backup"""
        try:
            self.manager = TelegramBackupManager()
        except ValueError as e:
            console.print(f"[red]Erro: {e}[/red]")
            console.print("[yellow]Por favor, configure suas credenciais no arquivo config.env[/yellow]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Erro ao inicializar: {e}[/red]")
            sys.exit(1)
    
    def show_welcome(self):
        """Mostra tela de boas-vindas"""
        welcome_text = Text()
        welcome_text.append("🚀 ", style="bold green")
        welcome_text.append("Telegram Backup Manager", style="bold cyan")
        welcome_text.append(" v2.0\n", style="dim")
        welcome_text.append("Sistema profissional de backup para Telegram", style="white")
        
        panel = Panel(
            welcome_text,
            title="[bold blue]Bem-vindo[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    def show_config(self):
        """Mostra configuração atual"""
        try:
            routes, filters = self.manager.load_config()
            stats = self.manager.get_stats()
            
            # Título
            console.print("[bold cyan]📋 Configuração Atual[/bold cyan]")
            console.print()
            
            # Estatísticas
            stats_columns = Columns([
                f"[green]✅ Rotas:[/green] {stats['total_routes']}",
                f"[blue]🎯 Filtros:[/blue] {stats['active_filters']}",
                f"[yellow]📊 Mensagens:[/yellow] {stats['processed_messages']}"
            ])
            
            console.print(stats_columns)
            console.print()
            
            # Tabela de rotas
            if routes:
                table = Table(title="Rotas de Backup")
                table.add_column("#", justify="right", style="cyan")
                table.add_column("Origem", style="green")
                table.add_column("Destino", style="blue")
                table.add_column("Status", justify="center")
                
                for idx, (source, dest) in enumerate(routes.items(), 1):
                    status = "✅ Ativa" if source in routes else "❌ Inativa"
                    table.add_row(str(idx), str(source), str(dest), status)
                
                console.print(table)
            else:
                console.print("[yellow]⚠️ Nenhuma rota configurada[/yellow]")
            
            console.print()
            
            # Filtros
            console.print("[bold cyan]🎯 Filtros:[/bold cyan]")
            for key, value in filters.items():
                status = "✅" if value else "❌"
                console.print(f"  {status} {key.replace('_', ' ').title()}")
            
            console.print()
        
        except Exception as e:
            console.print(f"[red]Erro ao mostrar configuração: {e}[/red]")
    
    def show_routes_table(self, routes: Dict = None):
        """Mostra tabela de rotas"""
        if routes is None:
            routes, _ = self.manager.load_config()
        
        if not routes:
            console.print("[yellow]Nenhuma rota configurada[/yellow]")
            return
        
        table = Table(title="Rotas de Backup (origem → destino)")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Origem", style="green")
        table.add_column("Destino", style="blue")
        table.add_column("Status", justify="center")
        
        for idx, (source, dest) in enumerate(routes.items(), 1):
            status = "✅ Ativa"
            table.add_row(str(idx), str(source), str(dest), status)
        
        console.print(table)
    
    def add_route_interactive(self):
        """Interface interativa para adicionar rota"""
        console.print("[bold cyan]➕ Adicionar Nova Rota[/bold cyan]")
        console.print()
        
        # Solicitar origem
        source = Prompt.ask("Origem (ID ou @username)", default="")
        if not source:
            console.print("[red]Origem é obrigatória[/red]")
            return
        
        # Solicitar destino
        dest = Prompt.ask("Destino", default="me")
        if not dest:
            console.print("[red]Destino é obrigatório[/red]")
            return
        
        # Confirmar
        if Confirm.ask(f"\nConfirmar rota: {source} → {dest}?"):
            with console.status("[bold green]Adicionando rota..."):
                if self.manager.add_route(source, dest):
                    console.print(f"[green]✅ Rota adicionada com sucesso![/green]")
                else:
                    console.print("[red]❌ Erro ao adicionar rota[/red]")
        
        console.print()
    
    def remove_route_interactive(self):
        """Interface interativa para remover rota"""
        routes, _ = self.manager.load_config()
        
        if not routes:
            console.print("[yellow]Nenhuma rota para remover[/yellow]")
            return
        
        console.print("[bold red]❌ Remover Rota[/bold red]")
        self.show_routes_table(routes)
        
        # Opções de remoção
        console.print("\n[dim]Digite o número da rota para remover, ou 'tudo' para remover todas[/dim]")
        choice = Prompt.ask("Seleção", default="")
        
        if choice.lower() in ["tudo", "all", "a"]:
            if Confirm.ask("⚠️ Remover TODAS as rotas?"):
                with console.status("[bold red]Removendo rotas..."):
                    self.manager.config.routes.clear()
                    self.manager.save_config()
                    console.print("[green]✅ Todas as rotas removidas![/green]")
        else:
            try:
                idx = int(choice)
                route_keys = list(routes.keys())
                if 1 <= idx <= len(route_keys):
                    source = route_keys[idx - 1]
                    dest = routes[source]
                    
                    if Confirm.ask(f"Remover rota: {source} → {dest}?"):
                        if self.manager.remove_route(source):
                            console.print("[green]✅ Rota removida com sucesso![/green]")
                        else:
                            console.print("[red]❌ Erro ao remover rota[/red]")
                else:
                    console.print("[red]Índice inválido[/red]")
            except ValueError:
                console.print("[red]Seleção inválida[/red]")
        
        console.print()
    
    def configure_filters_interactive(self):
        """Interface interativa para configurar filtros"""
        _, current_filters = self.manager.load_config()
        
        console.print("[bold cyan]⚙️ Configurar Filtros[/bold cyan]")
        console.print()
        
        # Configurações atuais
        console.print("[dim]Configurações atuais:[/dim]")
        for key, value in current_filters.items():
            status = "✅" if value else "❌"
            console.print(f"  {status} {key.replace('_', ' ').title()}")
        
        console.print()
        
        # Novas configurações
        media_only = Confirm.ask("Apenas mídia?", default=current_filters.get("media_only", False))
        photos = Confirm.ask("Incluir fotos?", default=current_filters.get("photos", True))
        videos = Confirm.ask("Incluir vídeos?", default=current_filters.get("videos", True))
        
        if Confirm.ask("\nSalvar configuração?"):
            with console.status("[bold green]Atualizando filtros..."):
                if self.manager.update_filters(
                    media_only=media_only,
                    photos=photos,
                    videos=videos
                ):
                    console.print("[green]✅ Filtros atualizados com sucesso![/green]")
                else:
                    console.print("[red]❌ Erro ao atualizar filtros[/red]")
        
        console.print()
    
    async def run_backup_service(self):
        """Executa o serviço de backup com interface Rich"""
        try:
            console.print("[bold green]🚀 Iniciando Serviço de Backup[/bold green]")
            
            # Status de conexão
            with console.status("[bold blue]Conectando ao Telegram..."):
                if not await self.manager.connect():
                    console.print("[red]❌ Erro ao conectar ao Telegram[/red]")
                    return
            
            console.print("[green]✅ Conectado com sucesso![/green]")
            
            # Informações do usuário
            me = await self.manager.client.get_me()
            console.print(f"[blue]Usuário:[/blue] {self.manager.get_entity_display_name(me)}")
            console.print()
            
            # Iniciar backup
            with Live(
                Panel(
                    Spinner("dots", text="Iniciando backup..."),
                    title="[bold yellow]Backup em Progresso[/bold yellow]"
                ),
                refresh_per_second=4
            ):
                if await self.manager.start_real_time_backup():
                    console.print("[green]✅ Backup iniciado![/green]")
                    console.print("[dim]Aguardando mensagens... (Ctrl+C para parar)[/dim]")
                    
                    try:
                        await self.manager.client.run_until_disconnected()
                    except KeyboardInterrupt:
                        console.print("\n[yellow]⚠️ Serviço interrompido pelo usuário[/yellow]")
                else:
                    console.print("[red]❌ Erro ao iniciar backup[/red]")
        
        except Exception as e:
            console.print(f"[red]❌ Erro no serviço: {e}[/red]")
        
        finally:
            await self.manager.disconnect()

# Comandos Click
@click.group()
@click.version_option(version="2.0.0")
def cli():
    """Telegram Backup CLI - Interface de linha de comando moderna"""
    pass

@cli.command()
def menu():
    """Interface interativa completa com menu Rich"""
    cli_interface = RichTelegramCLI()
    
    while True:
        cli_interface.show_welcome()
        
        # Menu principal
        console.print("[bold cyan]Opções:[/bold cyan]")
        console.print("[1] 📊 Ver configuração")
        console.print("[2] ➕ Adicionar rota")
        console.print("[3] ❌ Remover rota")
        console.print("[4] ⚙️ Configurar filtros")
        console.print("[5] 🚀 Iniciar backup")
        console.print("[6] 💾 Salvar configuração")
        console.print("[0] ❌ Sair")
        console.print()
        
        choice = Prompt.ask("Escolha", choices=["0", "1", "2", "3", "4", "5", "6"], default="1")
        
        if choice == "1":
            cli_interface.show_config()
        elif choice == "2":
            cli_interface.add_route_interactive()
        elif choice == "3":
            cli_interface.remove_route_interactive()
        elif choice == "4":
            cli_interface.configure_filters_interactive()
        elif choice == "5":
            asyncio.run(cli_interface.run_backup_service())
        elif choice == "6":
            if cli_interface.manager.save_config():
                console.print("[green]✅ Configuração salva![/green]")
            else:
                console.print("[red]❌ Erro ao salvar[/red]")
        elif choice == "0":
            console.print("[yellow]Saindo...[/yellow]")
            break
        
        console.print("\n" + "="*50 + "\n")

@cli.command()
def show_config():
    """Mostra configuração atual"""
    cli = RichTelegramCLI()
    cli.show_config()

@cli.command()
def add_route():
    """Adicionar rota interativamente"""
    cli = RichTelegramCLI()
    cli.add_route_interactive()

@cli.command()
def remove_route():
    """Remover rota interativamente"""
    cli = RichTelegramCLI()
    cli.remove_route_interactive()

@cli.command()
def run():
    """Executar backup diretamente"""
    console.print("[bold green]🚀 Iniciando backup...[/bold green]")
    run_backup()

@cli.command()
@click.option('--source', required=True, help='Origem (ID ou @username)')
@click.option('--dest', default='me', help='Destino (padrão: me)')
@click.option('--media-only', is_flag=True, help='Apenas mídia')
@click.option('--no-photos', is_flag=True, help='Desabilitar fotos')
@click.option('--no-videos', is_flag=True, help='Desabilitar vídeos')
def quick_backup(source, dest, media_only, no_photos, no_videos):
    """Backup rápido com parâmetros"""
    try:
        cli = RichTelegramCLI()
        
        # Configurar rota
        if cli.manager.add_route(source, dest):
            console.print(f"[green]✅ Rota {source} → {dest} configurada[/green]")
        
        # Configurar filtros
        filters = {
            "media_only": media_only,
            "photos": not no_photos,
            "videos": not no_videos
        }
        
        if cli.manager.update_filters(**filters):
            console.print("[green]✅ Filtros configurados[/green]")
        
        # Executar backup
        console.print("[bold green]🚀 Iniciando backup rápido...[/bold green]")
        asyncio.run(cli.run_backup_service())
    
    except Exception as e:
        console.print(f"[red]❌ Erro no backup rápido: {e}[/red]")

@cli.command()
@click.option('--config', help='Caminho para arquivo de configuração')
def setup(config):
    """Configurar sistema"""
    try:
        if config and os.path.exists(config):
            # Carregar configuração externa
            with open(config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            cli = RichTelegramCLI()
            cli.manager.config.routes = config_data.get("routes", {})
            cli.manager.config.filters.update(config_data.get("filters", {}))
            cli.manager.save_config()
            
            console.print("[green]✅ Configuração importada com sucesso![/green]")
        else:
            console.print("[yellow]Usando configuração padrão[/yellow]")
            # Criar configuração padrão
            cli = RichTelegramCLI()
            console.print("[green]✅ Configuração padrão criada[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Erro na configuração: {e}[/red]")

if __name__ == "__main__":
    cli()