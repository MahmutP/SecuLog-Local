# 🛡️ SecuLog Local

> **Track vulnerabilities efficiently & securely.**  
> **Zafiyetleri verimli ve güvenli bir şekilde takip edin.**

[![Python Badge](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database Badge](https://img.shields.io/badge/Database-SQLite-green?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License Badge](https://img.shields.io/badge/License-Apache%202.0-red?style=for-the-badge)](LICENSE)

**SecuLog Local**, siber güvenlik uzmanları ve pentesterlar için geliştirilmiş, komut satırı üzerinden çalışan (CLI), hafif ve %100 yerel (local) bir zafiyet takip sistemidir. Modern arayüzü ve veritabanı yapısı ile projelerinizi ve bulgularınızı organize etmenizi sağlar.

**SecuLog Local** is a lightweight, 100% local CLI vulnerability tracking system designed for cybersecurity professionals and pentesters. Organize your projects and findings with a modern interface and robust database architecture.

---

## 🌟 Features / Özellikler

| English (EN) 🇬🇧                                                       | Türkçe (TR) 🇹🇷                                                         |
| :------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| **Project Management:** Track multiple targets (Web, Mobile, etc.).  | **Proje Yönetimi:** Birden fazla hedefi (Web, Mobil vb.) takip edin.  |
| **Vulnerability Logging:** Add findings with Severity, CVSS & PoC.   | **Zafiyet Kaydı:** Şiddet, CVSS ve PoC detaylarıyla zafiyet ekleyin.  |
| **Advanced Console:** Tab-completion, history, and shell-like UX.    | **Gelişmiş Konsol:** Tab tamamlama, geçmiş ve shell benzeri deneyim.  |
| **Local Database:** Uses SQLite for fast and secure offline storage. | **Yerel Veritabanı:** Çevrimdışı, hızlı ve güvenli SQLite altyapısı.  |
| **Rich Interface:** Colored tables and banners via Rich library.     | **Zengin Arayüz:** Rich kütüphanesi ile renkli tablolar ve bannerlar. |

---

## 🚀 Installation / Kurulum

Prerequisites / Gereksinimler:
*   Python 3.8+

```bash
# 1. Clone the repository / Depoyu klonlayın
git clone https://github.com/MahmutP/SecuLog-Local.git
cd SecuLog-Local

# 2. Create Virtual Environment / Sanal ortam oluşturun (Recommended / Önerilen)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Requirements / Gereksinimleri yükleyin
pip install -r requirements.txt

# 4. Run the Tool / Aracı çalıştırın
python3 seculog_console.py
```

---

## 📖 Usage / Kullanım

SecuLog Local offers two interfaces. We recommend the **Advanced Console**.
SecuLog Local iki arayüz sunar. **Gelişmiş Konsol** kullanmanızı öneririz.

### Interactive Console (`seculog_console.py`)

Start the shell / Kabuğu başlatın:
`python3 seculog_console.py`

#### Commands / Komutlar:

*   `help` : List all commands. / Tüm komutları listeler.
*   `add_target <name> <url> <type>` : Add a new target. / Yeni hedef ekler.
    *   *Ex/Örn:* `add_target "My Bank" bank.com Web`
*   `show targets` : List all added targets in a table. / Tüm hedefleri tabloda gösterir.
*   `show vulns` : List all vulnerabilities. / Tüm zafiyetleri listeler.
*   `exit` : Close the application. / Uygulamadan çıkar.

---

## 🗄️ Database Structure / Veritabanı Yapısı

Bu proje **SQLite** ilişkisel veritabanı kullanır.  
This project uses **SQLite** relational database.

*   **Targets Table:** `ID`, `Name`, `URL`, `Type`
*   **Vulnerabilities Table:** `ID`, `Target_ID` (FK), `Title`, `Severity`, `CVSS`, `Status`

> For detailed SQL analysis, check [sql_code_analyze.md](sql_code_analyze.md).  
> Detaylı SQL analizi için [sql_code_analyze.md](sql_code_analyze.md) dosyasına bakın.

---

## ⚠️ Disclaimer / Yasal Uyarı

**TR:** Bu yazılım sadece eğitim amaçlı ve yasal güvenlik testlerinde (penetrasyon testleri) kullanılmak üzere geliştirilmiştir. Yetkisiz sistemlere karşı kullanımı yasa dışıdır ve geliştirici sorumluluk kabul etmez.

**EN:** This software is developed for educational purposes and authorized security testing (penetration testing) only. Usage against unauthorized systems is illegal, and the developer assumes no responsibility.

---

<p align="center">
  Developed by <b>MahmutP</b> with ❤️ and ☕
</p>
