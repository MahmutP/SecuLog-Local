# SecuLog-Local PostgreSQL Veritabanı Dokümantasyonu

Bu belge, uygulamanın kullandığı **PostgreSQL** veritabanı şemasını ve bu sunucuda (Docker) çalıştırılacak referans SQL komutlarını detaylandırır. Yeni platform mimarisi gereği SQLite komutları gerçek bir ilişkisel istemci-sunucu motoru olan PostgreSQL sentaksı ile harmanlanmıştır.

## PostgreSQL SQL Terimleri ve Anlamları

PostgreSQL üzerinde tablolar inşa edilirken kullanılan özel tipler ve anahtarlar aşağıda açıklanmıştır:

- **`SERIAL`**: (veya PostgreSQL 10 sonrasında daha modern adıyla `GENERATED ALWAYS AS IDENTITY`) Tam sayı (integer) tabanlı birincil anahtarlar (id) için otomatik artış fonksiyonu sağlar.
- **`VARCHAR`**: Belli bir karakter limitine (Örn: 255) kadar olan metin değerlerini saklar (isimler, başlıklar vb.).
- **`TEXT`**: Sınırsız veya çok uzun metinlerin (Log, PoC kodları, Rapor detayları) saklanması için kullanılır.
- **`TIMESTAMP`**: Tarih ve zamanı (Yıl-Ay-Gün Saat:Dakika:Saniye) saniye alt ölçeklerine kadar hatasız saklar.
- **`PRIMARY KEY`**: Her satırı benzersiz bir şekilde ayrıştıran benzersiz temel sütundur (genelde ID'ler tutar).
- **`FOREIGN KEY`**: Projeler tablosuyla Hedefler tablosu vb. arasında ilişki oluşturmak üzere başka tabloya yapılan referanstır.
- **`ON DELETE CASCADE`**: PostgreSQL'de ilişkisel bütünlük garantisidir. Bir ana Proje silinirse o projeye kayıtlı olan Zafiyetler ve Hedeflerin de yığıntı oluşturmaması için veri tabanı seviyesinde arka planda temizlenmesidir.

---

## Veritabanı Şeması Komutları (DB Oluşturma)

Docker konteynerına bağlandıktan sonra (örn: `psql -U seculog_user -d seculog`) arka planda Python uygulaması tarafından üretilecek olan iskelet SQL yapıları asgari düzeyde aşağıdaki gibi olacaktır.

### 1. Tablo: `projects` (Projeler Katmanı)
Ana çerçevedir. Sızma testinin tanımlandığı en üst birimdir.

```sql
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Tablo: `targets` (Hedefler)
Sızma testi projesinde taranacak cihaz, endpoint, sunucu veya web adreslerini projelere bağlar.

```sql
CREATE TABLE IF NOT EXISTS targets (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    description TEXT,
    criticality INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project
      FOREIGN KEY (project_id) 
      REFERENCES projects(id) 
      ON DELETE CASCADE
);
```

### 3. Tablo: `vulnerabilities` (Zafiyet Kayıtları)
Yapılan denemelerde tespit edilen güvenlik açıklarını hedefle ve projeyle ilişkilendirir.

```sql
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    target_id INTEGER,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(50) NOT NULL, 
    status VARCHAR(50) DEFAULT 'Open',
    poc TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_vuln
      FOREIGN KEY (project_id)
      REFERENCES projects(id)
      ON DELETE CASCADE,
    CONSTRAINT fk_target_vuln
      FOREIGN KEY (target_id)
      REFERENCES targets(id)
      ON DELETE SET NULL
);
```

---

## Basit Raporlama Sistemi SQL Komutları (Çalıştırılacak Sorgular)

API (Backend), basit raporlama verisini ön yüze sunarken veritabanından istatistik çekmek için bu tarz `SELECT` ifadelerini koşarak işlem yapacaktır.

### A) Bir Projedeki Mevcut Zafiyetlerin İstatistiklerini Hesaplama 
Hangi zafiyet tipinde (Critical, High, Medium) kaç adet mevcut açığımız olduğunu bulan raporlama grup sorgusu:

```sql
SELECT severity, COUNT(*) as vuln_count
FROM vulnerabilities
WHERE project_id = 1 AND status = 'Open'
GROUP BY severity
ORDER BY vuln_count DESC;
```
*(Sonuç Örneği: Critical > 3, High > 10 gibi rapor grafiklerini besler)*

### B) Rapor Ekranında Hedef Başına Zafiyetleri Listeleme
Hedef bilgisi (IP veya URL) ile zafiyet isimlerinin bir arada listelendiği klasik liste sorgusu:

```sql
SELECT t.name AS target_name, v.title, v.severity, v.status
FROM vulnerabilities v
JOIN targets t ON v.target_id = t.id
WHERE v.project_id = 1
ORDER BY 
   CASE v.severity 
     WHEN 'Critical' THEN 1 
     WHEN 'High' THEN 2 
     WHEN 'Medium' THEN 3 
     WHEN 'Low' THEN 4 
     ELSE 5 
   END;
```
*(Bu sayede rapor üretildiğinde React tarafına en kritik zafiyetlerden daha az kritik olanlara doğru sıralı temiz veri iletilir.)*
