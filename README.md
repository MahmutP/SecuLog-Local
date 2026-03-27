# SecuLog-Local 🛡️

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)

---

*[Scroll down for English version / İngilizce versiyonu için aşağı kaydırın ↓](#english-version)*

## Türkçe Versiyon 🇹🇷

**SecuLog-Local**, siber güvenlik uzmanlarının ve sistem yöneticilerinin, sızma testi (pentest) operasyonları sırasında tespit ettikleri zafiyetleri, hedefleri ve proje istatistiklerini izole, yerel (local) ve güvenli bir ortamda kayıt altına almalarını sağlayan modern bir bilgi sistemidir. 

### 🌟 Özellikler
- **Tam İzole Çalışma:** Tüm verileriniz makinenizde lokal olarak *(Docker Container ve Python venv)* izole çalışır, dışarıya hiçbir "hassas" veri gönderilmez.
- **İlişkisel İzlenebilirlik:** Projeler, projelerin içerisindeki hedefler (Targets) ve hedeflere bağlı zafiyetler (Vulnerabilities) bir döküm halinde güvenle tutulur.
- **Modern Arayüz:** Kullanıcı dostu ve Dark-Theme tabanlı, hızlı çalışan **React.js** web arayüzü.
- **Dinamik Raporlama Modülü:** Sızma testinin sonuçlarını, cihaz bazında zafiyet dağılımını analiz eden ve çıktıya/yazdırmaya (Print/PDF) hazır statik bir raporlama ekranı.

### 🏗️ Teknik Mimari
Sistem modern İstemci-Sunucu (Client-Server) mimarisinde çalışır:
- **Frontend (Tasarım ve Arayüz):** Node.js üzerine kurulu React.js (Vite ile oluşturulmuştur).
- **Backend (API Katmanı):** FastAPI (Python 3). (Veritabanı ilişkileri için SQLAlchemy ve Pydantic kullanılmıştır).
- **Database (Veritabanı Katmanı):** PostgreSQL (Tamamen Docker üzerinde koşar ve bağımlılık yaratmaz).

### 🚀 Başlangıç ve Kullanım Rehberleri
Projeyi bilgisayarınızda sadece birkaç komutla uçtan uca çalıştırabilmeniz ve kullanımınız bittiğinde sisteminizi yormadan her şeyi (container'ları ve volume'leri) silebilmeniz için detaylı bir rehber hazırladık:

👉 [Çalıştırma ve Temizlik Rehberi (Türkçe)](calistirma_ve_temizlik_rehberi.md)

Ayrıca veritabanındaki PostgreSQL komut yapılarını (Tablo şemaları ve RAW SQL sorgularını) ve mantığını incelemek isterseniz:

👉 [SQL ve Veritabanı Dokümantasyonu (Türkçe)](sql.md)

---

## English Version 🇬🇧 <a name="english-version"></a>

**SecuLog-Local** is a modern, web-based local information system designed for cybersecurity professionals and system administrators. It allows them to record and manage vulnerabilities, targets, and project statistics discovered during penetration testing operations in an isolated, local, and secure environment.

### 🌟 Features
- **Fully Isolated Environment:** All your data runs locally on your machine *(using Docker Containers and Python venv)*, ensuring that no sensitive data is transmitted outside.
- **Relational Traceability:** Projects, associated Targets, and linked Vulnerabilities are securely stored and mapped relationally for logical consistency.
- **Modern UI:** A user-friendly, high-performance, and dark-themed interface built with **React.js**.
- **Dynamic Reporting Module:** A built-in reporting screen that evaluates vulnerability distribution per target and is ready for print/PDF export dynamically.

### 🏗️ Technical Architecture
The system operates on a modern Client-Server architecture:
- **Frontend (UI Layer):** React.js (Bootstrapped with Vite) running on Node.js.
- **Backend (API Layer):** FastAPI (Python 3). (Using SQLAlchemy and Pydantic for data models).
- **Database (Data Layer):** PostgreSQL (Runs entirely inside a Docker container, leaving zero footprint on your host system).

### 🚀 Getting Started & Usage Guides
We have prepared a detailed step-by-step guide on how to spin up the project end-to-end via CLI in minutes, as well as how to completely clean up your system (destroying containers and volumes) when you are done:

👉 [Startup and Cleanup Guide (Turkish)](calistirma_ve_temizlik_rehberi.md)

If you would like to inspect the PostgreSQL database schemas and raw SQL queries used under the hood:

👉 [SQL and Database Documentation (Turkish)](sql.md)

---
**SecuLog-Local** - Built for streamlined and secure local pentest data tracking.
