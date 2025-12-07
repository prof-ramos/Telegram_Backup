#!/usr/bin/env python3
"""
Testes do Telegram Backup Manager
Script para verificar funcionamento do sistema
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

def test_imports():
    """Testa importações dos módulos principais"""
    print("🧪 Testando importações...")
    
    try:
        import streamlit
        print("✅ Streamlit importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Streamlit: {e}")
        return False
    
    try:
        import telethon
        print("✅ Telethon importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Telethon: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Pandas: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Plotly: {e}")
        return False
    
    try:
        import click
        print("✅ Click importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Click: {e}")
        return False
    
    try:
        import rich
        print("✅ Rich importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Rich: {e}")
        return False
    
    return True

def test_backend():
    """Testa o backend do sistema"""
    print("\n🧪 Testando backend...")
    
    try:
        from telegram_backup import TelegramBackupManager, BackupConfig
        print("✅ Backend importado com sucesso")
        
        # Testar configuração padrão
        config = BackupConfig.default()
        print(f"✅ Configuração padrão criada: {len(config.routes)} rotas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no backend: {e}")
        return False

def test_utils():
    """Testa utilitários"""
    print("\n🧪 Testando utilitários...")
    
    try:
        from utils import StreamlitUtils, get_system_info
        
        # Testar funções básicas
        info = get_system_info()
        print(f"✅ Informações do sistema: Python {info['python_version']}")
        
        # Testar formatação
        formatted_size = StreamlitUtils.format_file_size(1024)
        print(f"✅ Formatação de tamanho: {formatted_size}")
        
        # Testar validação de credenciais
        is_valid = StreamlitUtils.validate_telegram_credentials("123456", "abcdef1234567890abcdef1234567890")
        print(f"✅ Validação de credenciais: {'Válido' if is_valid else 'Inválido'}")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos utilitários: {e}")
        return False

def test_files():
    """Testa arquivos e diretórios"""
    print("\n🧪 Testando arquivos e diretórios...")
    
    # Verificar arquivos principais
    required_files = [
        "streamlit_app.py",
        "telegram_backup.py", 
        "cli.py",
        "utils.py",
        "requirements.txt",
        "pyproject.toml"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} não encontrado")
            return False
    
    # Verificar diretórios
    required_dirs = ["logs", "backups", ".streamlit"]
    
    for dir_name in required_dirs:
        path = Path(dir_name)
        try:
            path.mkdir(exist_ok=True)
            if path.exists():
                print(f"✅ Diretório {dir_name} disponível")
            else:
                print(f"❌ Diretório {dir_name} não foi criado")
                return False
        except Exception as e:
            print(f"❌ Diretório {dir_name} não pode ser criado: {e}")
            return False
    
    return True

def test_configuration():
    """Testa sistema de configuração"""
    print("\n🧪 Testando sistema de configuração...")
    
    try:
        # Criar configuração de teste
        test_config = {
            "routes": {
                "@test_channel": "me",
                "123456789": "backup_group"
            },
            "filters": {
                "media_only": False,
                "photos": True,
                "videos": True
            }
        }
        
        with open("test_config.json", "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=2)
        
        print("✅ Arquivo de configuração de teste criado")
        
        # Testar leitura
        with open("test_config.json", "r", encoding="utf-8") as f:
            loaded_config = json.load(f)
        
        print(f"✅ Configuração lida: {len(loaded_config['routes'])} rotas")
        
        # Limpar arquivo de teste
        os.remove("test_config.json")
        print("✅ Arquivo de teste limpo")
        
        return True
    except Exception as e:
        print(f"❌ Erro no teste de configuração: {e}")
        return False

def test_environment():
    """Testa variáveis de ambiente"""
    print("\n🧪 Testando variáveis de ambiente...")
    
    # Verificar config.env
    if os.path.exists("config.env"):
        print("✅ Arquivo config.env encontrado")
        
        # Verificar conteúdo
        with open("config.env", "r", encoding="utf-8") as f:
            content = f.read()
            if "API_ID" in content and "API_HASH" in content:
                print("✅ Variáveis de configuração presentes")
            else:
                print("⚠️ Variáveis de configuração não configuradas")
    else:
        print("⚠️ Arquivo config.env não encontrado")
    
    # Verificar variáveis do sistema
    python_path = os.environ.get("PYTHONPATH", "")
    if python_path:
        print(f"✅ PYTHONPATH configurado: {python_path[:50]}...")
    else:
        print("ℹ️ PYTHONPATH não configurado")
    
    return True

def test_streamlit_config():
    """Testa configuração do Streamlit"""
    print("\n🧪 Testando configuração do Streamlit...")
    
    config_path = ".streamlit/config.toml"
    if os.path.exists(config_path):
        print("✅ Configuração do Streamlit encontrada")
        
        # Verificar conteúdo básico
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "theme" in content and "server" in content:
                print("✅ Configuração básica presente")
            else:
                print("⚠️ Configuração pode estar incompleta")
    else:
        print("⚠️ Configuração do Streamlit não encontrada")
    
    return True

def test_dependencies():
    """Testa dependências do projeto"""
    print("\n🧪 Testando dependências...")
    
    try:
        # Verificar requirements.txt
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r", encoding="utf-8") as f:
                requirements = f.readlines()
            
            print(f"✅ requirements.txt com {len(requirements)} dependências")
            
            # Verificar dependências principais
            main_deps = ["streamlit", "telethon", "pandas", "plotly"]
            for dep in main_deps:
                found = any(dep in line.lower() for line in requirements)
                print(f"{'✅' if found else '❌'} {dep}")
        else:
            print("❌ requirements.txt não encontrado")
            return False
        
        # Verificar pyproject.toml
        if os.path.exists("pyproject.toml"):
            print("✅ pyproject.toml encontrado")
        else:
            print("⚠️ pyproject.toml não encontrado")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar dependências: {e}")
        return False

def test_scripts():
    """Testa scripts de execução"""
    print("\n🧪 Testando scripts de execução...")
    
    scripts = ["install.sh", "run.sh"]
    
    for script in scripts:
        if os.path.exists(script):
            # Verificar se é executável
            if os.access(script, os.X_OK):
                print(f"✅ {script} encontrado e executável")
            else:
                print(f"⚠️ {script} encontrado mas não executável")
        else:
            print(f"❌ {script} não encontrado")
    
    return True

def test_cli_functionality():
    """Testa funcionalidade básica da CLI"""
    print("\n🧪 Testando funcionalidade da CLI...")
    
    try:
        # Testar importação da CLI
        from cli import RichTelegramCLI
        
        # Criar instância (sem conectar)
        cli = RichTelegramCLI()
        
        print("✅ CLI inicializada com sucesso")
        print(f"✅ Manager criado: {type(cli.manager).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Erro na CLI: {e}")
        return False

def main():
    """Função principal de testes"""
    print("🚀 Telegram Backup Manager - Testes do Sistema")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Backend", test_backend),
        ("Utilitários", test_utils),
        ("Arquivos e Diretórios", test_files),
        ("Configuração", test_configuration),
        ("Variáveis de Ambiente", test_environment),
        ("Configuração Streamlit", test_streamlit_config),
        ("Dependências", test_dependencies),
        ("Scripts", test_scripts),
        ("Funcionalidade CLI", test_cli_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO DE TESTES")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📈 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está funcionando corretamente.")
        print("\nPróximos passos:")
        print("1. Configure suas credenciais no arquivo config.env")
        print("2. Execute: bash run.sh")
        print("3. Acesse: http://localhost:8501")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        print("\nDicas de solução:")
        print("- Execute: bash install.sh para instalar dependências")
        print("- Verifique se o Python 3.8+ está instalado")
        print("- Confira as mensagens de erro específicas")
    
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)