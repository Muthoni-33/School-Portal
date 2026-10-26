# 🏫 School Portal Monorepo Infrastructure

## 📝 Project Overview
This monorepo contains the decoupled backend microservices for the School Portal ecosystem. The application splits business domains into isolated backend engines to manage volatile user authentication traffic independently from structural classroom scheduling data.

---

## 🏗️ Architecture Overview
The application follows a distributed cloud-native architecture pattern:

* **Auth Service (`auth-service`):** Manages user verification, logins, and token signatures. Connected to an isolated authentication PostgreSQL DB schema.
* **Classes Service (`classes-service`):** Manages school course registries, timetables, and enrollments. Connected to an isolated academic PostgreSQL DB schema.

---

## 💻 Tech Stack & Components
* **Framework:** Flask API (Python 3.12)
* **Production Gateways:** Gunicorn (WSGI Server Process Multiplier)
* **Database Target:** PostgreSQL 15+ (Default Core Port `5432`)
* **Database Driver:** `psycopg2-binary`

---

## ⚙️ Pattern Implementation & Deployment Strategy

### Required Environment Configuration Matrix
Both services expect the following keys injected into their environment at container runtime via ConfigMaps and Secrets:

| Variable Name | Description | Source | Example Value |
| :--- | :--- | :--- | :--- |
| `DB_HOST` | Database Network Location | ConfigMap | `postgres-auth-svc` |
| `DB_PORT` | Port Target | ConfigMap | `5432` |
| `DB_NAME` | Database Name | ConfigMap | `school_portal_db` |
| `DB_USER` | Database Master Username | ConfigMap | `portal_admin` |
| `DB_PASSWORD` | Secure DB Credential Key | Secret | `SuperSecureSecret123!` |
