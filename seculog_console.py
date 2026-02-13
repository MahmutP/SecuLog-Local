import cmd2
from database.db_manager import connect_db
import sys

class SecuLogApp(cmd2.Cmd):
    intro = """
===================================================
   🛡️  SECULOG LOCAL - ADVANCED CONSOLE v1.0 🛡️
===================================================
Type 'help' or '?' to list commands.
Type 'exit' to close the application.
    """
    prompt = 'seculog > '

    def do_add_target(self, args):
        """
        Add a new target.
        Usage: add_target <name> <url> <type>
        Example: add_target 'My Site' example.com Web
        """
        try:
            # Basit argüman ayrıştırma
            parts = args.split()
            if len(parts) < 3:
                self.poutput("Usage: add_target <name> <url> <type>")
                return
            
            name = parts[0]
            url = parts[1]
            target_type = parts[2]

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO targets (name, target_url, target_type) VALUES (?, ?, ?)", 
                           (name, url, target_type))
            conn.commit()
            conn.close()
            self.poutput(f"[*] Target '{name}' added successfully.")
        except Exception as e:
            self.poutput(f"[!] Error: {e}")

    def do_show(self, args):
        """
        Show targets or vulnerabilities.
        Usage: show targets | show vulns
        """
        if args == 'targets':
            self._show_targets()
        elif args == 'vulns':
            self._show_vulns()
        else:
            self.poutput("Usage: show [targets|vulns]")

    def _show_targets(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, target_url, target_type FROM targets")
        targets = cursor.fetchall()
        conn.close()

        if not targets:
            self.poutput("No targets found.")
            return

        self.poutput(f"{'ID':<5} {'Name':<20} {'URL':<30} {'Type':<10}")
        self.poutput("-" * 65)
        for t in targets:
            self.poutput(f"{t[0]:<5} {t[1]:<20} {t[2]:<30} {t[3]:<10}")

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
            self.poutput("No vulnerabilities found.")
            return

        self.poutput(f"{'ID':<5} {'Target':<20} {'Vulnerability':<30} {'Severity':<10} {'CVSS'}")
        self.poutput("-" * 80)
        for v in vulns:
            self.poutput(f"{v[0]:<5} {v[1]:<20} {v[2]:<30} {v[3]:<10} {v[4]}")

    def do_exit(self, args):
        """Exit the application."""
        self.poutput("Goodbye!")
        return True

if __name__ == '__main__':
    app = SecuLogApp()
    sys.exit(app.cmdloop())
