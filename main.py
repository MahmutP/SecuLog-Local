import sys
from database.db_manager import connect_db

def print_banner():
    print("""
===================================================
   🛡️  SECULOG LOCAL - CLI v1.0  🛡️
===================================================
    """)

def add_target():
    print("\n--- Yeni Hedef Ekle ---")
    name = input("Hedef Adı (Örn: E-Ticaret): ").strip()
    if not name:
        print("Hata: Hedef adı boş olamaz!")
        return

    target_url = input("Hedef URL/IP (Örn: example.com): ").strip()
    target_type = input("Hedef Tipi (Web, Mobile, Network, IoT): ").strip()

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO targets (name, target_url, target_type) VALUES (?, ?, ?)", 
                       (name, target_url, target_type))
        conn.commit()
        print(f"Başarılı: '{name}' hedefi eklendi.")
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        conn.close()

def list_targets():
    print("\n--- Hedef Listesi ---")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, target_url, target_type FROM targets")
    targets = cursor.fetchall()
    conn.close()

    if not targets:
        print("Kayıtlı hedef yok.")
        return

    print(f"{'ID':<5} {'AD':<20} {'URL':<30} {'TIP':<10}")
    print("-" * 65)
    for t in targets:
        print(f"{t[0]:<5} {t[1]:<20} {t[2]:<30} {t[3]:<10}")

def add_vulnerability():
    list_targets()
    print("\n--- Zafiyet Ekle ---")
    
    try:
        target_id = int(input("Hedef ID: "))
    except ValueError:
        print("Hata: Geçersiz ID formatı.")
        return

    title = input("Zafiyet Başlığı: ").strip()
    severity = input("Şiddet (Critical, High, Medium, Low): ").strip()
    cvss = input("CVSS Skoru (0.0 - 10.0): ").strip()

    try:
        conn = connect_db()
        cursor = conn.cursor()
        # ID kontrolü
        cursor.execute("SELECT id FROM targets WHERE id = ?", (target_id,))
        if not cursor.fetchone():
            print("Hata: Belirtilen ID'ye sahip hedef bulunamadı.")
            conn.close()
            return

        cursor.execute('''
            INSERT INTO vulnerabilities (target_id, title, severity, cvss_score) 
            VALUES (?, ?, ?, ?)
        ''', (target_id, title, severity, float(cvss) if cvss else 0.0))
        conn.commit()
        print(f"Başarılı: Zafiyet '{title}' eklendi.")
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        conn.close()

def list_vulnerabilities():
    print("\n--- Zafiyet Listesi ---")
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
        print("Kayıtlı zafiyet yok.")
        return

    print(f"{'ID':<5} {'HEDEF':<20} {'ZAFIYET':<30} {'SEVIYE':<10} {'CVSS'}")
    print("-" * 80)
    for v in vulns:
        print(f"{v[0]:<5} {v[1]:<20} {v[2]:<30} {v[3]:<10} {v[4]}")

def main_menu():
    while True:
        print_banner()
        print("[1] Yeni Hedef Ekle (Add Target)")
        print("[2] Hedefleri Listele (List Targets)")
        print("[3] Zafiyet Ekle (Add Vulnerability)")
        print("[4] Zafiyetleri Listele (List Vulnerabilities)")
        print("[5] Çıkış (Exit)")
        
        choice = input("\nSeçiminiz: ")

        if choice == '1':
            add_target()
        elif choice == '2':
            list_targets()
        elif choice == '3':
            add_vulnerability()
        elif choice == '4':
            list_vulnerabilities()
        elif choice == '5':
            print("Çıkış yapılıyor...")
            sys.exit()
        else:
            print("Geçersiz seçim, tekrar deneyin.")
        
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main_menu()
