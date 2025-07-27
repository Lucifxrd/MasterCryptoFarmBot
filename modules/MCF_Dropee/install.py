#!/usr/bin/env python3
# Script de Instalação Automática - Dropee Bot Standalone
# Desenvolvido para facilitar a configuração inicial

import os
import sys
import json
import subprocess
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent

def print_banner():
    """Exibir banner de instalação"""
    print("=" * 60)
    print("🤖 DROPEE BOT STANDALONE - INSTALAÇÃO AUTOMÁTICA")
    print("=" * 60)
    print("📋 Este script vai configurar automaticamente o bot para você")
    print()

def check_python_version():
    """Verificar versão do Python"""
    print("🔍 Verificando versão do Python...")
    
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ é necessário!")
        print(f"   Versão atual: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} - OK")

def install_dependencies():
    """Instalar dependências necessárias"""
    print("\n📦 Instalando dependências...")
    
    requirements_file = MODULE_DIR / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ Arquivo requirements.txt não encontrado!")
        return False
    
    try:
        # Tentar instalar usando pip
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Dependências instaladas com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print("💡 Tente executar manualmente:")
        print(f"   pip install -r {requirements_file}")
        return False

def create_config_files():
    """Criar arquivos de configuração"""
    print("\n⚙️ Criando arquivos de configuração...")
    
    # Configuração principal
    config_file = MODULE_DIR / "config.json"
    if not config_file.exists():
        default_config = {
            "check_interval": 3600,
            "auto_claim_daily_reward": True,
            "auto_farming": True,
            "auto_tasks": True,
            "auto_wheel": True,
            "auto_upgrade": False,
            "delay_min": 5,
            "delay_max": 15,
            "max_retries": 3,
            "use_random_delays": True,
            "log_level": "INFO"
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Criado: {config_file}")
    else:
        print(f"⚠️  Já existe: {config_file}")
    
    # Arquivo de exemplo de contas
    accounts_example_file = MODULE_DIR / "accounts_example.json"
    if not accounts_example_file.exists():
        example_accounts = {
            "conta_principal": {
                "telegram_data": "query_id=AAAA...&user=%7B%22id%22%3A...",
                "proxy": None,
                "enabled": True,
                "notes": "Conta principal sem proxy"
            },
            "conta_com_proxy": {
                "telegram_data": "query_id=BBBB...&user=%7B%22id%22%3A...",
                "proxy": "http://usuario:senha@proxy:porta",
                "enabled": True,
                "notes": "Conta com proxy"
            },
            "conta_desabilitada": {
                "telegram_data": "query_id=CCCC...&user=%7B%22id%22%3A...",
                "proxy": None,
                "enabled": False,
                "notes": "Conta temporariamente desabilitada"
            }
        }
        
        with open(accounts_example_file, 'w', encoding='utf-8') as f:
            json.dump(example_accounts, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Criado: {accounts_example_file}")
    else:
        print(f"⚠️  Já existe: {accounts_example_file}")
    
    return True

def create_startup_script():
    """Criar script de inicialização"""
    print("\n🚀 Criando script de inicialização...")
    
    if os.name == 'nt':  # Windows
        startup_script = MODULE_DIR / "start_bot.bat"
        script_content = f"""@echo off
echo Iniciando Dropee Bot Standalone...
cd /d "{MODULE_DIR}"
python standalone_bot.py
pause
"""
    else:  # Linux/Mac
        startup_script = MODULE_DIR / "start_bot.sh"
        script_content = f"""#!/bin/bash
echo "Iniciando Dropee Bot Standalone..."
cd "{MODULE_DIR}"
python3 standalone_bot.py
"""
    
    with open(startup_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Dar permissão de execução no Linux/Mac
    if os.name != 'nt':
        os.chmod(startup_script, 0o755)
    
    print(f"✅ Criado: {startup_script}")
    return True

def show_next_steps():
    """Mostrar próximos passos"""
    print("\n" + "=" * 60)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print()
    
    print("1️⃣  CONFIGURAR CONTAS:")
    print(f"   • Copie: accounts_example.json → accounts.json")
    print(f"   • Edite accounts.json com seus dados do Telegram")
    print()
    
    print("2️⃣  OBTER DADOS DO TELEGRAM:")
    print("   • Abra Telegram Web/Desktop")
    print("   • Acesse @DropeeBot")
    print("   • Abra Developer Tools (F12)")
    print("   • Vá para aba Network")
    print("   • Clique em 'Play' no jogo")
    print("   • Procure requisição com 'query_id='")
    print("   • Copie toda a string de dados")
    print()
    
    print("3️⃣  EXECUTAR O BOT:")
    
    if os.name == 'nt':  # Windows
        print("   • Duplo clique em start_bot.bat")
        print("   • OU execute: python standalone_bot.py")
    else:  # Linux/Mac
        print("   • Execute: ./start_bot.sh")
        print("   • OU execute: python3 standalone_bot.py")
    
    print()
    print("4️⃣  COMANDOS ÚTEIS:")
    print("   • Ver estatísticas: python standalone_bot.py --stats")
    print("   • Versão avançada: python advanced_standalone_bot.py")
    print()
    
    print("📖 Para mais informações, consulte:")
    print("   • README_STANDALONE.md")
    print()
    
    print("💡 DICAS:")
    print("   • Configure proxies se necessário")
    print("   • Ajuste intervalos em config.json")
    print("   • Use a versão avançada para mais funcionalidades")
    print()
    
    print("🎯 BOT PRONTO PARA USO!")
    print("=" * 60)

def main():
    """Função principal de instalação"""
    try:
        print_banner()
        
        # Verificações
        check_python_version()
        
        # Instalações
        if not install_dependencies():
            print("\n⚠️  Instalação parcial - verifique dependências manualmente")
        
        # Configurações
        create_config_files()
        create_startup_script()
        
        # Próximos passos
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a instalação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()