from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion, NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from database.db_manager import connect_db
console = Console()

# --- Custom Completer with Meta Support ---
class MetaNestedCompleter(Completer):
    def __init__(self, options, meta_dict=None):
        self.options = options  # {key: sub_completer_or_dict_or_none}
        self.meta_dict = meta_dict or {}

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        
        # Context handling (Recurse if space exists)
        if ' ' in text:
            first_word, remaining = text.split(' ', 1)
            if first_word in self.options:
                sub = self.options[first_word]
                
                # Dynamic handling if sub is a dict (convert on the fly logic or expect Completer)
                completer = sub
                if isinstance(sub, dict):
                    # For simplicity, treat raw dicts as standard NestedCompleter without meta unless wrapped
                    completer = NestedCompleter.from_nested_dict(sub)
                
                if isinstance(completer, Completer):
                    new_document = Document(
                        remaining,
                        cursor_position=document.cursor_position - len(first_word) - 1
                    )
                    yield from completer.get_completions(new_document, complete_event)
            return

        # Current level completion
        word = document.get_word_before_cursor()
        for key in self.options:
            if key.startswith(word):
                meta = self.meta_dict.get(key)
                yield Completion(key, start_position=-len(word), display_meta=meta)

# Prompt Toolkit Style
style = Style.from_dict({
    'prompt': 'ansicyan bold',
    'output': '#af00ff',
})

import sys
from prompt_toolkit import PromptSession

# --- Helper Functions ---
def print_banner():
    banner_text = Text(justify="center")
    banner_text.append("\n🛡️  SECULOG LOCAL - TUI 🛡️\n", style="bold red")
    banner_text.append("Advanced Vulnerability Management System\n", style="bold white")
    banner_text.append("Powered by prompt_toolkit | Type 'help' for commands\n", style="dim green")
    
    panel = Panel(banner_text, border_style="cyan", expand=False)
    console.print(panel)


def get_vulns_for_completion():
    """Fetch vulnerability IDs and Titles for dynamic autocompletion."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM vulnerabilities")
        # Return dict {id: title} for description display
        vulns = {str(row[0]): row[1] for row in cursor.fetchall()}
        conn.close()
        return vulns
    except:
        return {}

def get_targets_for_completion():
    """Fetch target IDs and Names for dynamic autocompletion."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM targets")
        # Return dict {id: name} for description display
        targets = {str(row[0]): row[1] for row in cursor.fetchall()}
        conn.close()
        return targets # {id: name}
    except:
        return {}

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

def do_add_vuln(args):
    """usage: add_vuln <target_id> <title> <severity> <cvss>"""
    if len(args) < 4:
        console.print("[red]Usage: add_vuln <target_id> <title> <severity> <cvss>[/red]")
        return
    
    try:
        target_id = int(args[0])
        title = args[1]
        severity = args[2]
        cvss = float(args[3])
    except ValueError:
         console.print("[red]Error: Invalid format. Target ID must be int, CVSS must be float.[/red]")
         return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Check if target exists
        cursor.execute("SELECT id FROM targets WHERE id = ?", (target_id,))
        if not cursor.fetchone():
             console.print("[red]Error: Target ID not found.[/red]")
             conn.close()
             return

        cursor.execute('''
            INSERT INTO vulnerabilities (target_id, title, severity, cvss_score) 
            VALUES (?, ?, ?, ?)
        ''', (target_id, title, severity, cvss))
        conn.commit()
        conn.close()
        console.print(f"[bold green][+] Vulnerability '{title}' added successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red][!] Error:[/bold red] {e}")


def do_delete_target(args):
    """usage: delete_target <id>"""
    if not args:
        console.print("[red]Usage: delete_target <id>[/red]")
        return
    
    try:
        target_id = int(args[0])
        conn = connect_db()
        cursor = conn.cursor()
        
        # Check if target exists
        cursor.execute("SELECT name FROM targets WHERE id = ?", (target_id,))
        row = cursor.fetchone()
        if not row:
             console.print("[red]Error: Target ID not found.[/red]")
             conn.close()
             return
        
        name = row[0]
        # Delete vulnerabilities first (CASCADE usually handles this but let's be safe/explicit if FK not enforced)
        cursor.execute("DELETE FROM vulnerabilities WHERE target_id = ?", (target_id,))
        cursor.execute("DELETE FROM targets WHERE id = ?", (target_id,))
        
        conn.commit()
        conn.close()
        console.print(f"[bold green][+] Target '{name}' and its vulnerabilities deleted![/bold green]")
    except ValueError:
        console.print("[red]Error: ID must be an integer.[/red]")
    except Exception as e:
        console.print(f"[bold red][!] Error:[/bold red] {e}")

def do_delete_vuln(args):
    """usage: delete_vuln <id>"""
    if not args:
        console.print("[red]Usage: delete_vuln <id>[/red]")
        return

    try:
        vuln_id = int(args[0])
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM vulnerabilities WHERE id = ?", (vuln_id,))
        
        if cursor.rowcount == 0:
            console.print("[red]Error: Vulnerability ID not found.[/red]")
        else:
            conn.commit()
            console.print(f"[bold green][+] Vulnerability {vuln_id} deleted successfully![/bold green]")
        conn.close()
    except ValueError:
        console.print("[red]Error: ID must be an integer.[/red]")
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
        ("add_target", "Add a new target"),
        ("add_vuln", "Add a vulnerability (usage: add_vuln <id> <title> <sev> <cvss>)"),
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
    
    # MetaNestedCompleter requires:
    # 1. options: dict structure for nesting
    # 2. meta_dict: descriptions for current level keys
    
    # Base commands structure
    base_options = {
        'show': {'targets': None, 'vulns': None},
        'add_target': None,
        'add_vuln': None, # We will inject targets here dynamically
        'delete_target': None, # Dynamic injection
        'delete_vuln': None, # Dynamic injection
        'help': None,
        'exit': None,
        'clear': None,
    }

    # Meta descriptions for top-level commands
    base_meta = {
        'show': 'Show information (targets/vulns)',
        'add_target': 'Add a new target to database',
        'add_vuln': 'Add a vulnerability to a target',
        'delete_target': 'Delete a target by ID',
        'delete_vuln': 'Delete a vulnerability by ID',
        'help': 'Show help message',
        'exit': 'Exit the application',
        'clear': 'Clear terminal screen',
    }

    session = PromptSession(
        history=FileHistory('.seculog_history'),
        style=style
    )

    while True:
        try:
            # 1. Get current targets {id: name}
            targets_meta = get_targets_for_completion()
            vulns_meta = get_vulns_for_completion()
            
            # 2. Prepare options for dynamic commands
            target_ids_completer = MetaNestedCompleter(
                options={tid: None for tid in targets_meta.keys()}, 
                meta_dict=targets_meta
            )
            vuln_ids_completer = MetaNestedCompleter(
                options={vid: None for vid in vulns_meta.keys()}, 
                meta_dict=vulns_meta
            )
            
            # 3. Update base options 
            current_options = base_options.copy()
            current_options['add_vuln'] = target_ids_completer
            current_options['delete_target'] = target_ids_completer
            current_options['delete_vuln'] = vuln_ids_completer

            # 4. Create the main completer
            completer = MetaNestedCompleter(options=current_options, meta_dict=base_meta)
            
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
            elif cmd == 'add_vuln':
                do_add_vuln(args)
            elif cmd == 'delete_target':
                do_delete_target(args)
            elif cmd == 'delete_vuln':
                do_delete_vuln(args)
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
