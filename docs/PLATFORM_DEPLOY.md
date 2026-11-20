# 🌐 Men Tarmoq — Platforma arxitekturasi va o'rnatish qo'llanmasi

Ushbu hujjat platformani **VPS (public IP) + Home server (PPPoE internet)** infratuzilmasida
noldan ishga tushirishni bosqichma-bosqich tushuntiradi.

---

## 1. Arxitektura

```mermaid
flowchart LR
  subgraph INTERNET[Internet]
    S[Talaba brauzeri]
  end
  subgraph VPS["VPS (public IP)"]
    C[Caddy :443<br/>Let's Encrypt TLS]
    W[web: FastAPI platforma]
    D[(PostgreSQL)]
    C --> W --> D
  end
  subgraph HOME["Home server (PPPoE / CGNAT) → Proxmox → lab VM"]
    A[lab-agent :8090<br/>systemd]
    T[Traefik :8088]
    X[ttyd terminal<br/>har bir lab uchun]
    L[(containerlab<br/>FRR, Linux, ...)]
    A --> L
    T --> X --> L
  end
  S -->|HTTPS| C
  C -->|"/term/* (forward_auth → web)"| T
  W -->|"REST + Bearer token"| A
  HOME -. "WireGuard 10.99.0.0/24<br/>uydan VPS ga chiquvchi UDP 51820" .- VPS
```

| Komponent | Joylashuvi | Vazifasi |
|---|---|---|
| **web/** | VPS (Docker) | Kurslar, darslar (Markdown), testlar, progress, foydalanuvchilar, admin panel |
| **Caddy** | VPS (Docker) | HTTPS, `/term/*` uchun `forward_auth` (faqat lab egasi kira oladi) |
| **PostgreSQL** | VPS (Docker) | Foydalanuvchilar, progress, test natijalari, lab sessiyalar |
| **lab-agent/** | Home lab VM (systemd) | containerlab topologiyalarini ko'tarish/o'chirish, avto-tekshiruv, TTL |
| **Traefik** | Home lab VM (Docker) | `/term/<id>/` → tegishli ttyd konteyneriga dinamik yo'naltirish |
| **ttyd + lab-shell** | Home (har bir lab uchun konteyner) | Brauzerdagi terminal; faqat o'z lab tugunlariga `docker exec` |
| **WireGuard** | VPS ↔ Home | CGNAT ortidagi home serverni VPS ga ulaydi |

### Nega aynan shunday?

* **PPPoE + CGNAT:** uyga tashqaridan ulanib bo'lmaydi → home server VPS ga **o'zi** ulanadi (`PersistentKeepalive`).
* **Og'ir yuk uyda:** lablar ko'p RAM/CPU talab qiladi — home server buning uchun; kichik VPS faqat web va proxy.
* **Uy IP si yashirin:** internetga faqat VPS ko'rinadi.
* **Uy internet uzilsa:** platforma ishlashda davom etadi, faqat lablar vaqtincha "mavjud emas" bo'ladi.

### Lab hayot sikli

```mermaid
sequenceDiagram
  participant U as Talaba
  participant W as web (VPS)
  participant A as lab-agent (home)
  participant C as containerlab
  U->>W: POST /labs/start (ospf-triangle)
  W->>A: POST /labs {id, topology, ttl}
  A-->>W: 202 provisioning
  A->>C: deploy (alohida nom + mgmt subnet + CPU/RAM limit)
  A->>A: ttyd konteyner + Traefik label (/term/<id>)
  U->>W: GET /labs/<id>/status.json (polling)
  W->>A: GET /labs/<id> → running
  U->>W: /term/<id>/ (Caddy forward_auth ✓) → WireGuard → Traefik → ttyd
  U->>W: POST /labs/<id>/check
  W->>A: POST /labs/<id>/check (buyruqlar faqat lab.yaml dan)
  Note over A: TTL tugaganda yoki "Stop" bosilganda: containerlab destroy
```

---

## 2. Talablar

| | VPS | Home lab VM |
|---|---|---|
| OS | Ubuntu 22.04/24.04 | Ubuntu 24.04 (Proxmox VM tavsiya) |
| CPU / RAM | 1 vCPU / 1–2 GB | 4+ vCPU / 8–32 GB (≈ 0.5–1 GB har bir lab tuguniga) |
| Disk | 20 GB | 60+ GB (Docker imajlar) |
| Tarmoq | Public IPv4, 80/443/tcp, 51820/udp | Faqat chiquvchi internet (PPPoE/CGNAT bo'lsa ham bo'ladi) |
| Domen | `tarmoq.example.uz` → VPS IP (A yozuv) | — |

> ⚠️ **Xavfsizlik:** lablarni Proxmox host ning o'zida emas, **alohida VM** ichida ishga tushiring.
> Talabalar lab konteynerlarida root huquqiga ega — VM ularni uy tarmog'ingiz va hypervisordan ajratadi.
> VM ni alohida VLAN/bridge ga qo'yib, uy LAN iga yo'lni firewall bilan yoping.

---

## 3. O'rnatish (≈ 30 daqiqa)

### 3.1. VPS (boshqa Docker loyihalar bor bo'lsa ham xavfsiz)

```bash
sudo git clone https://github.com/sarvartech/pfsense-30-days.git /opt/men-tarmoq
cd /opt/men-tarmoq
sudo ./deploy/scripts/preflight-vps.sh     # FAQAT O'QIYDI: band portlar, konteynerlar, firewall, WireGuard
sudo ./deploy/scripts/setup-vps.sh          # MODE avtomatik: 80/443 band → proxy, bo'sh → caddy
```

`setup-vps.sh` mavjud loyihalarga tegmaydi:

| Nima | Qanday |
|---|---|
| Docker | O'rnatilgan bo'lsa — qayta o'rnatilmaydi, boshqa konteynerlarga tegilmaydi |
| Compose | Alohida loyiha `men-tarmoq`: konteynerlar `men-tarmoq-*`, tarmoq `men-tarmoq`, volume lar prefiksli |
| Portlar | `caddy` rejimi: 80/443 (faqat bo'sh bo'lsa). `proxy` rejimi: faqat `127.0.0.1:8010` |
| Firewall | `ufw enable`/`default deny` qilinmaydi; ufw faol bo'lsa faqat ruxsat qoidasi qo'shiladi |
| WireGuard | Alohida `wg-mt` interfeysi, UDP 51820 (band bo'lsa `WG_PORT=51821`), mavjud `wg0` ga tegilmaydi |
| Ishga tushirish | Avtomatik emas — `.env` ni tekshirganingizdan keyin qo'lda |

### 3.2. Home lab VM

```bash
sudo git clone https://github.com/sarvartech/pfsense-30-days.git /opt/men-tarmoq
cd /opt/men-tarmoq
sudo VPS_ENDPOINT=<VPS_IP>:<WG_PORT> VPS_PUBKEY=<VPS_PUBLIC_KEY> ./deploy/scripts/setup-home.sh
```

Skript oxirida **Home public key** va **AGENT_TOKEN** chiqadi.

### 3.3. VPS ga qaytib — tunnelni yakunlash va platformani ishga tushirish

```bash
sudo HOME_PUBKEY=<HOME_PUBLIC_KEY> ./deploy/scripts/setup-vps.sh
sudo wg show wg-mt                               # "latest handshake" bo'lishi kerak
ping -c2 10.99.0.2

sudo nano deploy/vps/.env                  # DOMAIN, ACME_EMAIL, ADMIN_EMAILS, LAB_AGENT_TOKEN=<AGENT_TOKEN>
cd deploy/vps && sudo docker compose up -d --build
```

Brauzerda `https://DOMAIN` ni oching → `ADMIN_EMAILS` dagi email bilan ro'yxatdan o'ting → **Admin** panelda
"Lab server: online" ko'rinishi kerak.

### 3.4. Tekshiruv ro'yxati

| Tekshiruv | Buyruq / joy | Kutilgan natija |
|---|---|---|
| Tunnel | VPS: `wg show` | latest handshake < 2 daqiqa |
| Agent | VPS: `curl -H "Authorization: Bearer $TOKEN" http://10.99.0.2:8090/health` | `{"ok":true,...}` |
| Traefik | VPS: `curl -I http://10.99.0.2:8088/term/x/` | `404` (Traefik javob beryapti) |
| Platforma | `https://DOMAIN/healthz` | `{"ok":true}` |
| Lab | Sayt → Laboratoriyalar → *Linux tarmoq asoslari* | Terminal 1–3 daqiqada ochiladi |

### 3.5. Proxy rejimi: mavjud reverse proxy orqali ulash

80/443 ni boshqa loyiha egallagan bo'lsa, platformaning Caddy si faqat `127.0.0.1:8010` da HTTP tinglaydi
(terminal ruxsat tekshiruvi ham shu Caddy ichida qoladi). Mavjud proxy da faqat bitta qoida qo'shasiz:
`DOMAIN → http://127.0.0.1:8010`, **Host** sarlavhasi va **WebSocket** saqlangan holda.

**Nginx (hostda o'rnatilgan):**

```nginx
server {
    listen 443 ssl http2;
    server_name tarmoq.example.uz;
    # ssl_certificate ... (certbot --nginx -d tarmoq.example.uz)

    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host;                       # MAJBURIY (CSRF tekshiruvi uchun)
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;                            # WebSocket (lab terminal)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
    }
}
```

**Nginx Proxy Manager (yoki konteynerdagi boshqa proxy):** konteyner hostning `127.0.0.1` iga yeta olmaydi,
shuning uchun `.env` da `PROXY_BIND=172.17.0.1` qo'ying (docker0 IP; faqat lokal Docker konteynerlarga ko'rinadi).
NPM da: Proxy Host → Domain `tarmoq.example.uz`, Forward `http` / `172.17.0.1` / `8010`,
✅ *Websockets Support*, SSL → Let's Encrypt.

**Traefik (Docker):** `men-tarmoq` tarmog'ini Traefik ga ulang va `men-tarmoq-caddy` konteyneriga label qo'shing
yoki file-provider bilan `http://127.0.0.1:8010` ga service yozing.

---

## 4. Kundalik boshqaruv

```bash
# Kontentni yangilash (yangi dars/kurs qo'shilganda)
cd /opt/men-tarmoq && git pull           # VPS da
# → Admin panel → "Kontentni qayta yuklash" (restart shart emas)
# Yangi lab qo'shilsa — home serverda ham git pull (agent labs/ ni diskdan o'qiydi)

# Loglar
docker compose -f deploy/vps/docker-compose.yml logs -f web     # VPS
journalctl -u men-tarmoq-agent -f                               # Home

# Zaxira nusxa (VPS)
docker compose -f deploy/vps/docker-compose.yml exec db pg_dump -U mentarmoq mentarmoq | gzip > backup-$(date +%F).sql.gz

# Osilib qolgan lablarni qo'lda tozalash (Home)
containerlab inspect --all
docker ps --filter label=men-tarmoq.lab
```

---

## 5. Kontent qo'shish

### 5.1. Yangi dars

1. `courses/<kurs>/lessons/NN-nom.md` yarating:

   ```markdown
   ---
   title: "OSPF multi-area"
   duration: 50
   lab: ospf-triangle          # ixtiyoriy — labs/ dagi nom
   quiz:
     - q: "ABR nima?"
       options: ["Area Border Router", "Autonomous Border Router", "..."]
       answer: 0               # 0 dan boshlanadigan indeks
       explain: "Bir nechta area ga ulangan router."
   ---

   # OSPF multi-area
   Matn, jadvallar, ```mermaid diagrammalar, kod bloklari...
   ```

2. `courses/<kurs>/course.yaml` da tegishli modulga qo'shing:
   `- {slug: ospf-areas, file: lessons/03-ospf-areas.md}`

Faylda yo'q darslar saytda **"tez orada"** sifatida ko'rinadi — shuning uchun avval reja (course.yaml), keyin matn yozish qulay.

### 5.2. Yangi kurs

`courses/<slug>/course.yaml` (namuna: `courses/routing/course.yaml`). `status: soon` — katalogda "Tez orada" belgisi.

### 5.3. Yangi laboratoriya

```
labs/<nom>/
├── topology.clab.yml   # containerlab topologiyasi (nodes, links, binds, exec)
├── lab.yaml            # sarlavha, tugunlar (shell), avto-tekshiruvlar
├── README.md           # talabaga ko'rsatiladigan topshiriqlar
└── ...                 # konfiguratsiya fayllari (daemons, r1.conf ...)
```

`lab.yaml` dagi tekshiruv: `node` ichida `cmd` bajariladi, natija `expect` (regex) ga mos kelsa ✓.
Agent bu buyruqlarni **faqat diskdagi lab.yaml dan** o'qiydi — tarmoq orqali buyruq qabul qilmaydi.

**Vendor imajlari (MikroTik CHR, Cisco IOL, Arista cEOS, Juniper vJunos):** litsenziya talablari sababli
repoda yo'q. [vrnetlab](https://github.com/hellt/vrnetlab) bilan o'zingiz build qilib, home serverga yuklang
va topologiyada `kind: mikrotik_ros` / `kind: cisco_iol` / `kind: ceos` ishlating.

**pfSense lablari:** pfSense konteynerda ishlamaydi — 30 kunlik kurs lablari Proxmox VM larida bajariladi
(qarang: `LAB_TOPOLOGY.md`). Kelajakda: Proxmox API orqali VM klonlash moduli.

---

## 6. Lokal ishlab chiqish

```bash
cd web
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
ADMIN_EMAILS=siz@example.com uvicorn app.main:app --reload   # http://127.0.0.1:8000  (SQLite, lablarsiz)
pytest -q                                                   # web testlari
cd ../lab-agent && pip install -r requirements.txt pytest && pytest -q
```

---

## 7. Yo'l xaritasi (keyingi bosqichlar)

- [ ] "Tez orada" darslar matnini yozish (har bir kurs bo'yicha)
- [ ] MikroTik CHR va Cisco IOL lablari (vrnetlab)
- [ ] pfSense lablari uchun Proxmox API orqali VM klonlash
- [ ] Sertifikat (kurs tugatilganda PDF)
- [ ] Telegram bot orqali bildirishnomalar va login
- [ ] Bir nechta lab-server (home + qo'shimcha VPS) — navbat/scheduler
