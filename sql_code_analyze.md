# SQL Analiz Dokümantasyonu

Bu doküman, SecuLog Local projesinde kullanılan SQL komutlarını ve bunların teknik analizlerini içerir.

## 1. Tablo Oluşturma: Targets (Hedefler)

**SQL Kodu:**
```sql
CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    target_url TEXT UNIQUE,
    target_type TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Analiz:**
*   **Amaç:** Penetrasyon testi yapılacak hedef sistemleri (Domain, IP, API vb.) saklamak.
*   **Kritik Noktalar:**
    *   `id`: Her hedef için benzersiz bir kimlik sağlar.
    *   `target_url UNIQUE`: Aynı URL'in mükerrer kaydedilmesini engeller.
    *   `created_at DEFAULT CURRENT_TIMESTAMP`: Kayıt anındaki zamanı otomatik ekler.

## 2. Tablo Oluşturma: Vulnerabilities (Zafiyetler)

**SQL Kodu:**
```sql
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    cvss_score REAL,
    vuln_type TEXT,
    description TEXT,
    poc_steps TEXT,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (target_id) REFERENCES targets(id) ON DELETE CASCADE
);
```

**Analiz:**
*   **Amaç:** Tespit edilen zafiyetlerin detaylarını saklamak ve ilgili hedefe bağlamak.
*   **Kritik Noktalar:**
    *   `FOREIGN KEY (target_id)`: Bu zafiyetin hangi hedefe ait olduğunu belirtir.
    *   `ON DELETE CASCADE`: Eğer bir hedef (`target`) silinirse, ona bağlı tüm zafiyetler de otomatik olarak silinir. Bu, veritabanında "öksüz kayıt" (orphan record) kalmasını önler.
    *   `PRAGMA foreign_keys = ON`: SQLite'ta bu özelliğin kod tarafında aktif edilmesi gerekmektedir.

## 3. Opsiyonel: Veri Ekleme (INSERT) Testi

**SQL Kodu:**
```sql
INSERT INTO targets (name, target_url, target_type) VALUES (?, ?, ?);
```

**Analiz:**
*   **Amaç:** Yeni bir hedef eklemek.
*   **Güvenlik:** `?` işareti (placeholder) kullanılarak SQL Injection saldırılarına karşı koruma sağlanır (Parameterized Query).

## 4. Veri Listeleme: Zafiyetleri Hedef Adıyla Getirme (JOIN)

**SQL Kodu:**
```sql
SELECT v.id, t.name, v.title, v.severity, v.cvss_score 
FROM vulnerabilities v
JOIN targets t ON v.target_id = t.id;
```

**Analiz:**
*   **Amaç:** Kullanıcıya zafiyet listesini gösterirken, sadece `target_id` (örn: 1) göstermek yerine, o ID'ye karşılık gelen Hedef Adını (örn: "E-Ticaret") göstermek.
*   **Yöntem:** `JOIN targets t ON v.target_id = t.id` ifadesi ile iki tablo ilişkilendirilerek okunabilir veri elde edilir.
