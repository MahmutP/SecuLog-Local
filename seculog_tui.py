import sys
import shlex
from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion, NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
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
                
                # Dynamic handling if sub is a dict
                completer = sub
                if isinstance(sub, dict):
                    # Pass down the meta dict for the next level if exists
                    # Improve: We need a way to pass nested meta. 
                    # Current implementation only supports top-level meta.
                    # Let's check if self.meta_dict has nested structure for this key.
                    
                    next_meta = {}
                    # If meta_dict[first_word] is a dict, use it.
                    if isinstance(self.meta_dict.get(first_word), dict):
                        next_meta = self.meta_dict.get(first_word)
                        
                    completer = MetaNestedCompleter(sub, meta_dict=next_meta)
                
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
                # Meta can be a string (description) or a dict (nested descriptions)
                # If it's a dict, we might want to show a generic description or nothing for the key itself
                meta = self.meta_dict.get(key)
                if isinstance(meta, dict):
                    meta = meta.get('__self__', 'Subcommands available') # Placeholder
                
                yield Completion(key, start_position=-len(word), display_meta=meta)

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

def do_update_target(args):
    """usage: update_target <id>"""
    if not args:
        console.print("[red]Usage: update_target <id>[/red]")
        return
    
    try:
        target_id = int(args[0])
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, target_url, target_type FROM targets WHERE id = ?", (target_id,))
        row = cursor.fetchone()
        if not row:
            console.print("[red]Error: Target ID not found.[/red]")
            conn.close()
            return

        current_name, current_url, current_type = row
        console.print(f"[cyan]Updating Target {target_id} (Press Enter to keep current value)[/cyan]")
        
        # Interactive prompts
        # We need a temporary session for this or just input() but input() lacks style.
        # We can reuse the session passed to main if we refactor, but for now simple input is easier or creating a new prompt session.
        # Let's use simple input() for simplicity or a local PromptSession.
        # A local session is better.
        temp_session = PromptSession(style=style)
        
        new_name = temp_session.prompt(f"Name [{current_name}]: ").strip() or current_name
        new_url = temp_session.prompt(f"URL [{current_url}]: ").strip() or current_url
        new_type = temp_session.prompt(f"Type [{current_type}]: ").strip() or current_type
        
        cursor.execute("UPDATE targets SET name=?, target_url=?, target_type=? WHERE id=?", 
                       (new_name, new_url, new_type, target_id))
        conn.commit()
        conn.close()
        console.print(f"[bold green][+] Target {target_id} updated successfully![/bold green]")
        
    except ValueError:
        console.print("[red]Error: ID must be an integer.[/red]")
    except Exception as e:
        console.print(f"[bold red][!] Error:[/bold red] {e}")

def do_update_vuln(args):
    """usage: update_vuln <id>"""
    if not args:
        console.print("[red]Usage: update_vuln <id>[/red]")
        return
    
    try:
        vuln_id = int(args[0])
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT title, severity, cvss_score FROM vulnerabilities WHERE id = ?", (vuln_id,))
        row = cursor.fetchone()
        if not row:
            console.print("[red]Error: Vulnerability ID not found.[/red]")
            conn.close()
            return

        curr_title, curr_sev, curr_cvss = row
        console.print(f"[cyan]Updating Vulnerability {vuln_id} (Press Enter to keep current value)[/cyan]")
        
        temp_session = PromptSession(style=style)
        
        new_title = temp_session.prompt(f"Title [{curr_title}]: ").strip() or curr_title
        new_sev = temp_session.prompt(f"Severity [{curr_sev}]: ").strip() or curr_sev
        new_cvss_str = temp_session.prompt(f"CVSS [{curr_cvss}]: ").strip()
        
        new_cvss = float(new_cvss_str) if new_cvss_str else curr_cvss
        
        cursor.execute("UPDATE vulnerabilities SET title=?, severity=?, cvss_score=? WHERE id=?", 
                       (new_title, new_sev, new_cvss, vuln_id))
        conn.commit()
        conn.close()
        console.print(f"[bold green][+] Vulnerability {vuln_id} updated successfully![/bold green]")
        
    except ValueError:
        console.print("[red]Error: Invalid format.[/red]")
    except Exception as e:
        console.print(f"[bold red][!] Error:[/bold red] {e}")

def do_show_all():
    """Show tree view of targets and vulns"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get all targets
    cursor.execute("SELECT id, name, target_type FROM targets")
    targets = cursor.fetchall()
    
    if not targets:
        console.print("[yellow]No data found.[/yellow]")
        conn.close()
        return

    root = Tree("🛡️  [bold white]SecuLog Data Tree[/bold white]")

    for t_id, t_name, t_type in targets:
        target_node = root.add(f"[bold cyan]{t_name}[/bold cyan] [dim]({t_type})[/dim] [yellow][ID: {t_id}][/yellow]")
        
        # Get vulns for this target
        cursor.execute("SELECT id, title, severity, cvss_score FROM vulnerabilities WHERE target_id=?", (t_id,))
        vulns = cursor.fetchall()
        
        if not vulns:
            target_node.add("[dim italic]No vulnerabilities[/dim italic]")
        else:
            for v_id, v_title, v_sev, v_cvss in vulns:
                # Colorize severity
                sev_style = "green"
                if v_sev.lower() == "critical": sev_style = "bold red"
                elif v_sev.lower() == "high": sev_style = "red"
                elif v_sev.lower() == "medium": sev_style = "yellow"
                
                target_node.add(f"[bold white]{v_title}[/bold white] - [{sev_style}]{v_sev}[/{sev_style}] (CVSS: {v_cvss}) [dim][ID: {v_id}][/dim]")

    conn.close()
    console.print(root)

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
        ("update_target", "Update target details (usage: update_target <id>)"),
        ("delete_target", "Delete a target (usage: delete_target <id>)"),
        ("add_vuln", "Add a vulnerability (usage: add_vuln <t_id> <title> <sev> <cvss>)"),
        ("update_vuln", "Update vulnerability details (usage: update_vuln <id>)"),
        ("delete_vuln", "Delete a vulnerability (usage: delete_vuln <id>)"),
        ("show targets", "List all registered targets"),
        ("show vulns", "List all vulnerabilities"),
        ("show all", "Show hierarchical tree view of targets and vulnerabilities"),
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
        'show': {'targets': None, 'vulns': None, 'all': None},
        'add_target': None,
        'update_target': None, # Dynamic
        'add_vuln': None, # We will inject targets here dynamically
        'update_vuln': None, # Dynamic injection
        'delete_target': None, # Dynamic injection
        'delete_vuln': None, # Dynamic injection
        'help': None,
        'exit': None,
        'clear': None,
    }

    # Meta descriptions for top-level commands
    base_meta = {
        'show': {
            '__self__': 'Show information',
            'targets': 'List all registered targets',
            'vulns': 'List all vulnerabilities',
            'all': 'Show hierarchical tree view'
        },
        'add_target': 'Add a new target to database',
        'update_target': 'Update target details',
        'add_vuln': 'Add a vulnerability to a target',
        'update_vuln': 'Update vulnerability details',
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
            # 1. Get dynamic data
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
            current_options['update_target'] = target_ids_completer
            
            current_options['delete_vuln'] = vuln_ids_completer
            current_options['update_vuln'] = vuln_ids_completer

            # 4. Create the main completer
            completer = MetaNestedCompleter(options=current_options, meta_dict=base_meta)
            
            text = session.prompt('seculog > ', completer=completer)
            text = text.strip()
            
            if not text:
                continue
            
            # Use shlex for correct argument parsing (quotes handling)
            try:
                parts = shlex.split(text)
            except ValueError:
                console.print("[red]Error: Unmatched quote[/red]")
                continue
                
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
            elif cmd == 'update_target':
                do_update_target(args)
            elif cmd == 'add_vuln':
                do_add_vuln(args)
            elif cmd == 'update_vuln':
                do_update_vuln(args)
            elif cmd == 'delete_target':
                do_delete_target(args)
            elif cmd == 'delete_vuln':
                do_delete_vuln(args)
            elif cmd == 'show':
                if len(args) > 0 and args[0] == 'targets':
                    do_show_targets()
                elif len(args) > 0 and args[0] == 'vulns':
                    do_show_vulns()
                elif len(args) > 0 and args[0] == 'all':
                    do_show_all()
                else:
                    console.print("[red]Invalid show command. Try 'show targets', 'show vulns', or 'show all'.[/red]")
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
