#!/usr/bin/env python3
# Script Principal de Execução - Dropee Bot Standalone
# Oferece múltiplas opções de execução

import sys
import os
import time
import argparse
import asyncio
from pathlib import Path

# Adicionar o diretório atual ao path
MODULE_DIR = Path(__file__).resolve().parent
sys.path.append(str(MODULE_DIR))

def print_banner():
    """Exibir banner principal"""
    print("🤖 DROPEE BOT STANDALONE")
    print("=" * 50)
    print("Versão: 2.0 | Autor: Baseado no trabalho do MasterkinG32")
    print("=" * 50)

def check_files():
    """Verificar se arquivos necessários existem"""
    required_files = [
        "standalone_bot.py",
        "advanced_standalone_bot.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (MODULE_DIR / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Arquivos necessários não encontrados:")
        for file in missing_files:
            print(f"   • {file}")
        print("\n💡 Execute o install.py primeiro")
        return False
    
    return True

def run_simple_bot():
    """Executar bot simples"""
    print("🚀 Executando bot simples...")
    try:
        from standalone_bot import run_bot
        asyncio.run(run_bot())
    except ImportError as e:
        print(f"❌ Erro ao importar bot simples: {e}")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

def run_advanced_bot():
    """Executar bot avançado"""
    print("🚀 Executando bot avançado...")
    try:
        from advanced_standalone_bot import run_advanced_bot
        asyncio.run(run_advanced_bot())
    except ImportError as e:
        print(f"❌ Erro ao importar bot avançado: {e}")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

def show_stats():
    """Mostrar estatísticas"""
    try:
        from advanced_standalone_bot import show_stats
        show_stats()
    except ImportError:
        print("❌ Módulo de estatísticas não disponível")
    except Exception as e:
        print(f"❌ Erro ao mostrar estatísticas: {e}")

def run_continuous(bot_type="advanced", interval=3600):
    """Executar bot continuamente"""
    print(f"🔄 Executando bot {bot_type} continuamente (intervalo: {interval}s)")
    print("⚠️  Use Ctrl+C para parar")
    
    cycle = 1
    
    try:
        while True:
            print(f"\n🔄 CICLO {cycle} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if bot_type == "simple":
                run_simple_bot()
            else:
                run_advanced_bot()
            
            print(f"\n⏳ Aguardando {interval}s até o próximo ciclo...")
            print(f"📅 Próxima execução: {time.strftime('%H:%M:%S', time.localtime(time.time() + interval))}")
            
            time.sleep(interval)
            cycle += 1
            
    except KeyboardInterrupt:
        print(f"\n🛑 Bot parado pelo usuário após {cycle-1} ciclos")

def show_menu():
    """Mostrar menu interativo"""
    while True:
        print("\n" + "=" * 50)
        print("📋 MENU PRINCIPAL")
        print("=" * 50)
        print("1️⃣  Executar Bot Simples")
        print("2️⃣  Executar Bot Avançado")
        print("3️⃣  Executar Continuamente (Avançado)")
        print("4️⃣  Executar Continuamente (Simples)")
        print("5️⃣  Ver Estatísticas")
        print("6️⃣  Configurações")
        print("0️⃣  Sair")
        print("=" * 50)
        
        try:
            choice = input("👉 Escolha uma opção: ").strip()
            
            if choice == "1":
                run_simple_bot()
            elif choice == "2":
                run_advanced_bot()
            elif choice == "3":
                interval = input("⏰ Intervalo em segundos (padrão 3600): ").strip()
                interval = int(interval) if interval.isdigit() else 3600
                run_continuous("advanced", interval)
            elif choice == "4":
                interval = input("⏰ Intervalo em segundos (padrão 3600): ").strip()
                interval = int(interval) if interval.isdigit() else 3600
                run_continuous("simple", interval)
            elif choice == "5":
                show_stats()
            elif choice == "6":
                show_config_menu()
            elif choice == "0":
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except ValueError:
            print("❌ Digite um número válido!")

def show_config_menu():
    """Mostrar menu de configurações"""
    print("\n📁 ARQUIVOS DE CONFIGURAÇÃO")
    print("-" * 30)
    
    config_files = [
        ("accounts.json", "Contas do Telegram"),
        ("config.json", "Configurações do bot"),
        ("tokens.json", "Tokens salvos"),
        ("stats.json", "Estatísticas")
    ]
    
    for file, description in config_files:
        file_path = MODULE_DIR / file
        status = "✅ Existe" if file_path.exists() else "❌ Não existe"
        size = f"({file_path.stat().st_size} bytes)" if file_path.exists() else ""
        print(f"• {file:<15} - {description:<20} {status} {size}")
    
    print("\n💡 DICAS:")
    print("• Copie accounts_example.json para accounts.json")
    print("• Configure seus dados do Telegram em accounts.json")
    print("• Ajuste configurações em config.json")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Dropee Bot Standalone - Script de Execução",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["simple", "advanced", "stats", "continuous", "menu"],
        default="menu",
        help="Modo de execução"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Intervalo para modo contínuo (segundos)"
    )
    
    parser.add_argument(
        "--bot-type",
        choices=["simple", "advanced"],
        default="advanced",
        help="Tipo de bot para modo contínuo"
    )
    
    args = parser.parse_args()
    
    # Configurar encoding
    try:
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass
    
    print_banner()
    
    # Verificar arquivos
    if not check_files():
        return
    
    # Executar modo escolhido
    try:
        if args.mode == "simple":
            run_simple_bot()
        elif args.mode == "advanced":
            run_advanced_bot()
        elif args.mode == "stats":
            show_stats()
        elif args.mode == "continuous":
            run_continuous(args.bot_type, args.interval)
        else:  # menu
            show_menu()
            
    except KeyboardInterrupt:
        print("\n👋 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()