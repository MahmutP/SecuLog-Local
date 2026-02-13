import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from database.db_manager import connect_db

# Rich Console Setup
console = Console()

# Prompt Toolkit Style
style = Style.from_dict({
    'prompt': 'ansicyan bold',
    'output': '#af00ff',
})

# --- Helper Functions ---
def print_banner():
    banner_text = Text(justify="center")
    banner_text.append("\n🛡️  SECULOG LOCAL - TUI 🛡️\n", style="bold red")
    banner_text.append("Advanced Vulnerability Management System\n", style="bold white")
    banner_text.append("Powered by prompt_toolkit | Type 'help' for commands\n", style="dim green")
    
    panel = Panel(banner_text, border_style="cyan", expand=False)
    console.print(panel)

def get_targets_for_completion():
    """Fetch target names for dynamic autocompletion."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM targets")
        targets = [row[0] for row in cursor.fetchall()]
        conn.close()
        return targets
    except:
        return []

# --- Business Logic ---
def do_add_target(args):
    """usage: add_target <name> <url> <type>"""
    if len(args) < 3:
        console.print("[red]Usage: add_target <name> <url> <type>[/red]")
        return
    
    name, url, t_type = args[0], args[1], args[2]
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO targets (name, target_url, target_type) VALUES (?, ?, ?)", 
                       (name, url, t_type))
        conn.commit()
        conn.close()
        console.print(f"[bold green][+] Target '{name}' added successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red][!] Error:[/bold red] {e}")

def do_show_targets():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, target_url, target_type FROM targets")
    targets = cursor.fetchall()
    conn.close()

    if not targets:
        console.print("[yellow]No targets found.[/yellow]")
        return

    table = Table(title="🎯 Registered Targets", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Name", style="green")
    table.add_column("URL", style="yellow")
    table.add_column("Type", style="blue")

    for t in targets:
        table.add_row(str(t[0]), t[1], t[2], t[3])
    console.print(table)

def do_show_vulns():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id, t.name, v.title, v.severity, v.cvss_score 
        FROM vulnerabilities v
        JOIN targets t ON v.target_id = t.id
    ''')
    vulns = cursor.fetchall()
    conn.close()

    if not vulns:
        console.print("[yellow]No vulnerabilities found.[/yellow]")
        return

    table = Table(title="🐛 Vulnerability Report", show_header=True, header_style="bold red")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Target", style="green")
    table.add_column("Vulnerability", style="white")
    table.add_column("Severity", justify="center")
    table.add_column("CVSS", justify="right")

    for v in vulns:
        severity = v[3]
        sev_style = "green"
        if severity.lower() == "critical": sev_style = "bold red"
        elif severity.lower() == "high": sev_style = "red"
        elif severity.lower() == "medium": sev_style = "yellow"
        table.add_row(str(v[0]), v[1], v[2], Text(severity, style=sev_style), str(v[4]))
    console.print(table)

def do_help():
    table = Table(title="Available Commands", show_header=True, header_style="bold blue")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    
    commands = [
        ("add_target", "Add a new target (usage: add_target <name> <url> <type>)"),
        ("show targets", "List all registered targets"),
        ("show vulns", "List all vulnerabilities"),
        ("clear", "Clear the screen"),
        ("exit", "Exit the application"),
        ("help", "Show this help message")
    ]
    
    for cmd, desc in commands:
        table.add_row(cmd, desc)
    console.print(table)

# --- Main Interaction Loop ---
def main():
    print_banner()
    
    # Nested Completer for subcommands
    completer = NestedCompleter.from_nested_dict({
        'show': {'targets': None, 'vulns': None},
        'add_target': None,
        'help': None,
        'exit': None,
        'clear': None,
    })

    session = PromptSession(
        history=FileHistory('.seculog_history'),
        style=style
    )

    while True:
        try:
            text = session.prompt('seculog > ', completer=completer)
            text = text.strip()
            
            if not text:
                continue
            
            parts = text.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == 'exit':
                console.print("[bold red]Goodbye![/bold red]")
                sys.exit(0)
            elif cmd == 'clear':
                print("\033c", end="")
            elif cmd == 'help':
                do_help()
            elif cmd == 'add_target':
                do_add_target(args)
            elif cmd == 'show':
                if len(args) > 0 and args[0] == 'targets':
                    do_show_targets()
                elif len(args) > 0 and args[0] == 'vulns':
                    do_show_vulns()
                else:
                    console.print("[red]Invalid show command. Try 'show targets' or 'show vulns'.[/red]")
            else:
                console.print(f"[red]Unknown command: {cmd}[/red]")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
