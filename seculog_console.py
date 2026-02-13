import cmd2
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from database.db_manager import connect_db
import sys

console = Console()

class SecuLogApp(cmd2.Cmd):
    def __init__(self):
        # Set consistent persistent history file
        super().__init__(persistent_history_file='~/.seculog_history')
        self.prompt = 'seculog > '
        # Remove default commands that clutter the help screen
        self.hidden_commands = ['alias', 'macro', 'run_pyscript', 'run_script', 'shortcuts', 'edit']

    # --- Banner & Intro ---
    def intro_banner(self):
        banner_text = Text(justify="center")
        banner_text.append("\n🛡️  SECULOG LOCAL 🛡️\n", style="bold red")
        banner_text.append("Advanced Vulnerability Management System\n", style="bold white")
        banner_text.append("v1.0.0 | Type 'help -v' for verbose commands\n", style="dim cyan")
        
        panel = Panel(banner_text, border_style="red", expand=False)
        console.print(panel)

    def preloop(self):
        self.intro_banner()

    # --- Add Target Command ---
    add_target_parser = cmd2.Cmd2ArgumentParser(description="Add a new target to the database.")
    add_target_parser.add_argument('name', help="Name of the target (e.g., 'E-Commerce Site')")
    add_target_parser.add_argument('url', help="URL or IP address of the target")
    add_target_parser.add_argument('type', help="Type of target (Web, Mobile, etc.)")

    @cmd2.with_argparser(add_target_parser)
    def do_add_target(self, args):
        """Add a new target to the database."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO targets (name, target_url, target_type) VALUES (?, ?, ?)", 
                           (args.name, args.url, args.type))
            conn.commit()
            conn.close()
            console.print(f"[bold green][+] Target '{args.name}' added successfully![/bold green]")
        except Exception as e:
            console.print(f"[bold red][!] Error:[/bold red] {e}")

    # --- Show Command ---
    show_parser = cmd2.Cmd2ArgumentParser(description="Display targets or vulnerabilities.")
    show_subparsers = show_parser.add_subparsers(title="subcommands", help="sub-command help")

    # show targets
    show_targets_parser = show_subparsers.add_parser('targets', help="List all registered targets")
    
    # show vulns
    show_vulns_parser = show_subparsers.add_parser('vulns', help="List all vulnerabilities")
    show_vulns_parser.add_argument('-t', '--target', type=int, help="Filter vulnerabilities by Target ID")

    @cmd2.with_argparser(show_parser)
    def do_show(self, args):
        """Show targets or vulnerabilities with formatted tables."""
        # args namespace comes from the subparser. 
        # Check which subcommand was called by inspecting args attributes or passed command
        # cmd2 argparse integration handles this dynamically.
        
        # Since we use subparsers, we need to know which one was selected.
        # But cmd2's handling with subparsers is a bit tricky in one method.
        # A clearer pattern in cmd2 is to use distinct methods or check attributes.
        # Here we will check the 'func' attribute if we were using set_defaults, 
        # or simply check the command line string in a raw 'do_show'.
        # However, purely with argparser decorator:
        
        # Let's simplify: check sys.argv logic inside? No.
        # Check the 'subcommand' name manually? 
        # Actually, let's look at the subcommand parsers.
        pass
    
    # Redefine show command without subparser decorator for simpler logic first, 
    # or use separate commands like `show_targets` and alias them. 
    # But user wants `show targets`.
    
    # Recommended Cmd2 pattern for 'show <subcommand>':
    def do_show(self, args):
        """
        Show information about targets or vulnerabilities.
        Usage: show targets | show vulns
        """
        if not args:
            self.do_help('show')
            return

        argv = args.split()
        subcmd = argv[0].lower()

        if subcmd == 'targets':
            self._show_targets()
        elif subcmd == 'vulns':
            self._show_vulns()
        else:
            console.print(f"[red]Unknown subcommand: {subcmd}[/red]")
            console.print("Valid subcommands: targets, vulns")

    def _show_targets(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, target_url, target_type FROM targets")
        targets = cursor.fetchall()
        conn.close()

        if not targets:
            console.print("[yellow]No targets found. Use 'add_target' to create one.[/yellow]")
            return

        table = Table(title="🎯 Registered Targets", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Name", style="green")
        table.add_column("URL / IP", style="yellow")
        table.add_column("Type", style="blue")

        for t in targets:
            table.add_row(str(t[0]), t[1], t[2], t[3])
        
        console.print(table)

    def _show_vulns(self):
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
            # Colorize severity
            severity = v[3]
            sev_style = "green"
            if severity.lower() == "critical": sev_style = "bold red"
            elif severity.lower() == "high": sev_style = "red"
            elif severity.lower() == "medium": sev_style = "yellow"
            
            table.add_row(str(v[0]), v[1], v[2], Text(severity, style=sev_style), str(v[4]))
        
        console.print(table)

    # --- Other Commands ---
    def do_exit(self, args):
        """Exit the application."""
        console.print("[bold red]Goodbye![/bold red]")
        return True

if __name__ == '__main__':
    app = SecuLogApp()
    sys.exit(app.cmdloop())
