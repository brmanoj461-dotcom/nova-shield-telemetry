# 🛡️ Nova-Shield: Secure Multi-Tenant Telemetry Hub

Nova-Shield is an enterprise-grade, lightweight SaaS network logging and telemetry ingestion engine. Built with **FastAPI** and backed by a robust **SQLite** database, it allows multiple tenants to securely stream log payloads using authenticated HTTP header verification.

The hub features a real-time responsive analytics dashboard powered by **Tailwind CSS** that pulls live database changes every 2 seconds without requiring any page reloads.

---

## 🚀 Key Architectural Features

* **Multi-Tenant Isolation:** Validates incoming streams by cross-referencing tenant identifiers with registered secrets in a secure database.
* **Header-Based Authentication:** Employs secure `X-API-Key` validation inside HTTP request headers to reject unauthorized log spoofing.
* **SQLite Relational Storage:** Replaced flat-file log storage with structured database indexes, ensuring highly performant querying.
* **Real-Time Polling UI:** Features an executive dark-mode command center displaying live counters for log streams, active nodes, and active critical security incidents.

---

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **Database:** SQLite3
* **Frontend:** HTML5, Tailwind CSS, JavaScript (Fetch API / Polling)

---

## 📦 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/nova-shield-telemetry.git](https://github.com/your-username/nova-shield-telemetry.git)
   cd nova-shield-telemetry