# -*- coding: utf-8 -*-
"""
Full enrichment of HAProxy, High Availability (CARP), Multi-WAN, and VPN modules.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODULES = {}

# ==========================================
# DAY 08: Multi-WAN
# ==========================================
MODULES[8] = {
    "lecture": """# 📚 [KUN-08] LECTURE: Multi-WAN Masterclass — Dual ISP Failover, Policy-Based Routing va Load Balancing

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Korxonada internet uzilishlariga barham berish (99.99% Uptime), bir vaqtning o'zida ikkita turli texnologiyadagi provayderlarni (Optika + Zaxira LTE/Optika) ulash, trafikni aqlli taqsimlash (Load Balancing) va avtomatik zaxiraga o'tish (Failover) arxitekturasini o'rganish.

---

## 🧭 Mundarija
1. [Multi-WAN Arxitekturasi va Korxona Ehtiyoji](#1-multi-wan-arxitekturasi-va-korxona-ehtiyoji)
2. [dpinger va Gateway Monitoring Mexanizmi](#2-dpinger-va-gateway-monitoring-mexanizmi)
3. [Gateway Groups Mantiqi: Tiering va Triggers](#3-gateway-groups-mantiqi-tiering-va-triggers)
4. [Policy-Based Routing (PBR) va Qoidalar Tartibi](#4-policy-based-routing-pbr-va-qoidalar-tartibi)
5. [Sticky Connections va Sessiyalar Saqlanishi](#5-sticky-connections-va-sessiyalar-saqlanishi)
6. [CARP Klasterida Multi-WAN Qanday Tashkil Etiladi?](#6-carp-klasterida-multi-wan-qanday-tashkil-etiladi)
7. [Inbound Multi-WAN (DNS Round-Robin va Port Forward)](#7-inbound-multi-wan)
8. [Xulosa va O'z-o'zini Tekshirish](#8-xulosa)

---

## 1. Multi-WAN Arxitekturasi va Korxona Ehtiyoji

Zamonaviy biznesda 1 soatlik internet uzilishi (Downtime) kompaniyaga millionlab so'm zarar, to'xtab qolgan to'lov terminallari, yetib bormagan bank o'tkazmalari va qoniqarsiz mijozlarni anglatadi. Yagona internet provayderiga (SPOF - Single Point of Failure) bog'lanib qolish jiddiy xatodir.

Multi-WAN konsepsiyasi kamida ikkita mustaqil ISP kanalini pfSense ga ulashni nazarda tutadi:
* **Asosiy Provayder (ISP-1 / Primary):** Katta tezlikdagi optik tolali kanal (masalan, 200 Mbps).
* **Zaxira Provayder (ISP-2 / Secondary):** Mustaqil boshqa aloqa operatori (masalan, ikkinchi optika yoki 4G/5G LTE/Mikroto'lqinli radio-kanal).

```mermaid
flowchart TD
    ISP1["ISP-1 (Optika - 200 Mbps)\nGateway: 192.168.100.1"] -->|WAN1: igb0| PFS["pfSense Multi-WAN Gateway"]
    ISP2["ISP-2 (Zaxira LTE/Optika - 50 Mbps)\nGateway: 192.168.200.1"] -->|WAN2: igb1| PFS
    PFS -->|dpinger ICMP Probe 1.1.1.1| ISP1
    PFS -->|dpinger ICMP Probe 8.8.8.8| ISP2
    PFS -->|LAN: igb2| CORP["Korporativ Tarmoq (10.10.10.0/24)"]
    PFS -->|DMZ: igb3| SERVERS["Serverlar Segmenti (10.10.20.0/24)"]
```

---

## 2. dpinger va Gateway Monitoring Mexanizmi

pfSense har bir shlyuzning holatini FreeBSD ning maxsus `dpinger` servisi orqali har soniyada tekshirib turadi:
* **Monitor IP:** Shlyuzning o'zini emas, internetdagi global va ishonchli IP manzillarni tekshirish shart. Chunki provayder modemi ishlab turgan bo'lsa-da, tashqi magistral uzilgan bo'lishi mumkin.
  * WAN1 uchun: `1.1.1.1` (Cloudflare)
  * WAN2 uchun: `8.8.8.8` (Google)
* **Thresholds (Chegaralar):**
  * **Latency:** Standart holatda 500ms dan oshsa, kanal sekinlashgan deb hisoblanadi.
  * **Packet Loss:** 20% dan ortiq paket yo'qolsa, kanal yaroqsiz deb baholanadi.

---

## 3. Gateway Groups Mantiqi: Tiering va Triggers

pfSense shlyuzlarni guruhlash uchun `Gateway Groups` vositasidan foydalanadi:

| Rejim Nomi | WAN1 Tier | WAN2 Tier | Trigger | Ishlash Printsipi |
|---|:---:|:---:|---|---|
| **Failover (Active/Passive)** | **Tier 1** | **Tier 2** | `Member Down` | Barcha trafik WAN1 orqali ketadi. Faqat WAN1 o'chgandagina WAN2 ga o'tiladi. |
| **Load Balancing (Active/Active)** | **Tier 1** | **Tier 1** | `Packet Loss or High Latency` | Paketlar oqimi ikkala kanal bo'yicha teng (yoki og'irligiga qarab) taqsimlanadi. |
| **Degraded Failover** | **Tier 1** | **Tier 2** | `Packet Loss` | Agar WAN1 da paket yo'qotish 10% dan oshsa, avtomat WAN2 ga o'tiladi. |

---

## 4. Policy-Based Routing (PBR) va Qoidalar Tartibi

pfSense da standart holatda barcha trafik tizimning `Default Gateway` si orqali chiqadi. Shlyuz guruhlarini ishlatish uchun **Policy-Based Routing (PBR)** qoidalari yoziladi:

> [!WARNING]
> **Kritik Xato:** Agar LAN interfeysida eng yuqori qoidaga Gateway sifatida `GW_GROUP` qo'yilsa, ichki tarmoqlararo (Inter-VLAN) va pfSense ning o'ziga boruvchi (DNS) so'rovlar ham tashqi internetga yo'naltirilib uzilib qoladi!

### To'g'ri Qoidalar Tartibi:
1. **Pass Rule (Local Traffic):** Destination: `LAN Subnets / RFC1918_Subnets` -> Gateway: `Default` (Ichki trafik router ichida qolsin).
2. **Pass Rule (Local DNS):** Destination: `This Firewall (self)`, Port: `53` -> Gateway: `Default`.
3. **Pass Rule (Internet PBR):** Destination: `*` (Any), Gateway: `GW_FAILOVER` yoki `GW_LOADBALANCE`.

---

## 5. Sticky Connections va Sessiyalar Saqlanishi

Load Balancing (Round-Robin) rejimida ikkala provayder parallel ishlayotganda quyidagi muammo yuzaga keladi:
* Foydalanuvchi Bank saytiga yoki korporativ CRM ga kirganda, birinchi so'rov WAN1 (IP: `203.0.113.5`) orqali boradi.
* Keyingi sahifani yuklaganda PBR so'rovni WAN2 (IP: `198.51.100.14`) ga tashlaydi.
* Bank tizimi bitta sessiyada mijoz IP manzili birdaniga o'zgarib ketganini ko'rib, xavfsizlik vajidan sessiyani bekor qiladi (Logout).

**Yechim:** `System -> Advanced -> Miscellaneous` bo'limida **`Use sticky connections`** parametrini yoqish. pfSense mijozning IP manzilini xotiraga oladi va uning barcha tashqi sessiyalarini belgilangan vaqt davomida (masalan, 300 soniya) aynan bitta WAN kanali orqali jo'natadi.

---

## 6. CARP Klasterida Multi-WAN Qanday Tashkil Etiladi?

Yuqori barqarorlikdagi (CARP) ikkita firewall mavjud bo'lganda, har ikkala firewall ikkala provayderga ulanishi shart:
* **Arxitektura:** Provayder-1 kabeli kichik L2 switchga (yoki VLAN 100 ga) ulanadi. Switchdan ikkita kabel chiqib, FW-01 WAN1 ga va FW-02 WAN1 ga boradi.
* Provayder-2 ham alohida switchga (yoki VLAN 200 ga) ulanadi va FW-01 WAN2 hamda FW-02 WAN2 ga boradi.
* Har bir provayder segmentida **CARP VIP** olinadi (masalan, WAN1 CARP VIP va WAN2 CARP VIP).
* Barcha chiquvchi NAT qoidalari shaxsiy interfeys IP ga emas, aynan tegishli CARP VIP ga bog'lanadi.

---

## 7. Inbound Multi-WAN

Agar ichki DMZ da Web-server joylashgan bo'lsa va unga tashqaridan ikkala provayder orqali kirish kerak bo'lsa:
1. Har ikkala WAN da alohida Port Forward qoidasi yaratiladi.
2. Tashqi domenga (masalan `www.company.uz`) ikkita DNS `A` yozuvi biriktiriladi:
   * `A www.company.uz 203.0.113.5` (ISP1)
   * `A www.company.uz 198.51.100.14` (ISP2)
3. pfSense dagi `reply-to` mexanizmi tufayli: WAN1 dan kirib kelgan paketga javob majburiy ravishda WAN1 orqali, WAN2 dan kirgan so'rovga javob esa WAN2 orqali qaytariladi!

---

## 8. Xulosa
Multi-WAN — korxonaning uzluksiz ishlash kafolatidir. To'g'ri sozlangan dpinger, PBR va Sticky Connections tizimi foydalanuvchilarga sezdirmasdan avariya holatlarini yengib o'tish imkonini beradi.
""",

    "lab": """# 🛠️ [KUN-08] LAB: Dual ISP Failover va Policy-Based Load Balancing Amaliyoti

**Mavzu:** 2 ta provayderni ulash, Gateway Groups, PBR va jonli Failover testi  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyaning yagona optik tolali internet kanali ekskavator simni uzib yuborishi oqibatida 4 soatga o'chib qoldi. Barcha savdo terminallari, ombor logistikasi va call-markaz to'xtab, kompaniya katta moliyaviy zarar ko'rdi. Rahbariyat zaxira 4G/LTE provayderini ulab, optika uzilganda 5 soniya ichida avtomatik zaxiraga o'tadigan va optika qaytganda asosiy liniyaga qaytadigan tizim qurishni talab qildi.

---

## 🗺️ 2. Topologiya va IP Rejasi

```mermaid
flowchart LR
    ISP1["ISP-1 (Primary): 192.168.100.1"] -->|WAN1: vtnet0 / igb0| PF["pfSense Multi-WAN"]
    ISP2["ISP-2 (Backup): 192.168.200.1"] -->|WAN2: vtnet2 / igb1| PF
    PF -->|LAN: vtnet1 / igb2 (10.10.10.1)| SW["L2 Switch"]
    SW --> PC1["Admin PC (10.10.10.50)"]
    SW --> PC2["Ofis PC (10.10.10.60)"]
```

### 📋 Interfeyslar Jadvali
| Interfeys | Jismoniy Port | Virtual Port | IP Manzil / CIDR | Gateway | Vazifasi |
|---|---|---|---|---|---|
| `WAN1` | `igb0` | `vtnet0` | `192.168.100.2/24` | `192.168.100.1` | Asosiy provayder (Optika) |
| `WAN2` | `igb1` | `vtnet2` | `192.168.200.2/24` | `192.168.200.1` | Zaxira provayder (LTE) |
| `LAN` | `igb2` | `vtnet1` | `10.10.10.1/24` | - | Korporativ ofis tarmog'i |

---

## 🖥️ 3. Talaba Laboratoriya Muhiti

### 🔹 VARIANT A: Real Jismoniy pfSense (Mini-PC)
* Mini-PC da kamida 3 ta port bo'lishi shart (`igb0`, `igb1`, `igb2`).
* `igb0` ga asosiy provayder kabelini, `igb1` ga zaxira modem (LAN porti) kabelini ulang.
* Har bir modem turli IP subnet tarqatayotganiga ishonch hosil qiling (masalan biri 192.168.1.1, ikkinchisi 192.168.8.1).

### 🔹 VARIANT B: Virtual Muhit (Proxmox VE / VMware)
* **Proxmox:** pfSense VM ga 3 ta tarmoq kartasi bering:
  * `net0` -> `vmbr0` (WAN1: 192.168.100.0/24)
  * `net1` -> `vmbr1` (LAN: 10.10.10.0/24)
  * `net2` -> `vmbr2` (WAN2: 192.168.200.0/24 - alohida Linux Bridge)

---

## ⚙️ 4. Qadam-baqadam Sozlash

### 1-Qadam: WAN2 Interfeysini Faollashtirish
1. `Interfaces -> Assignments` bo'limiga kiring.
2. `Available network ports` qatoridan uchinchi portni tanlab, **Add** tugmasini bosing.
3. Yangi paydo bo'lgan `OPT1` interfeysiga kiring, **Enable Interface** ni yoqing.
4. Description: `WAN2_BACKUP`.
5. IPv4 Configuration Type: `Static IPv4` (yoki DHCP).
6. IPv4 Address: `192.168.200.2/24`.
7. IPv4 Upstream Gateway: `Add a new gateway` -> Name: `WAN2_GW`, Gateway IP: `192.168.200.1`. Saqlang va Apply qiling.

### 2-Qadam: Gateway Monitoring Sozlash
1. `System -> Routing -> Gateways` bo'limiga o'ting.
2. `WAN_GW` (WAN1) ni tahrirlang:
   * Monitor IP: `1.1.1.1`
3. `WAN2_GW` (WAN2) ni tahrirlang:
   * Monitor IP: `8.8.8.8`
4. Apply Changes tugmasini bosing. `Status -> Gateways` da ikkala shlyuz ham Online bo'lishi kerak.

### 3-Qadam: Shlyuz Guruhlarini (Gateway Groups) Yaratish
1. `System -> Routing -> Gateway Groups` yorlig'iga o'ting.
2. **Failover Guruhini yaratish:**
   * Group Name: `GW_FAILOVER`
   * `WAN_GW`: **Tier 1**
   * `WAN2_GW`: **Tier 2**
   * Trigger Level: `Member Down`
   * Description: `Primary WAN1 failover to Backup WAN2`
3. **Load Balancing Guruhini yaratish:**
   * Group Name: `GW_LOADBALANCE`
   * `WAN_GW`: **Tier 1**
   * `WAN2_GW`: **Tier 1**
   * Trigger Level: `Packet Loss or High Latency`
   * Description: `Active-Active Equal Cost Traffic Sharing`

### 4-Qadam: Sticky Connections Yoqish
1. `System -> Advanced -> Miscellaneous` bo'limiga kiring.
2. `Load Balancing` bloki ostidagi **Use sticky connections** katakchasini yoqing.
3. Source tracking timeout: `300` soniya. Saqlang.

### 5-Qadam: Policy-Based Routing (PBR) Qoidalarini Tuzish
1. `Firewall -> Rules -> LAN` ga kiring.
2. **Kritik Qoida 1 (Ichki tarmoqlar uchun):**
   * Action: `Pass`, Source: `LAN net`, Destination: `RFC1918_Subnets` (yoki LAN subnets).
   * Gateway: `default` (hech qanday guruh qo'yilmaydi!).
3. **Kritik Qoida 2 (Internet trafigi uchun):**
   * Standart `Default allow LAN to any rule` qoidasini tahrirlang.
   * `Display Advanced` tugmasini bosing.
   * Pastga tushib, **Gateway** maydonida `GW_FAILOVER` (yoki `GW_LOADBALANCE`) ni tanlang.
   * Saqlang va **Apply Changes** qiling.

---

## 🧪 5. Verifikatsiya va Jonli Sinovlar

### 1. Joriy Shlyuzni Tekshirish:
Mijoz kompyuterdan joriy tashqi IP ni aniqlang:
```bash
curl https://ifconfig.me
```

### 2. Avariya (Failover) Sinovi:
1. Mijoz kompyuterida uzluksiz ping ishga tushiring:
```bash
ping -t 8.8.8.8
```
2. pfSense konsolidan yoki VM sozlamalaridan WAN1 virtual adapterini uzing (yoki fizik WAN1 kabelini sug'uring).
3. `Status -> Gateways` ga qarang: WAN1 darhol **Offline** holatiga o'tadi.
4. Ping oynasiga qarang: faqat 1 yoki 2 ta paket yo'qoladi (`Request timed out`), keyin ping darhol davom etadi!
5. Chiqish IP sini qayta tekshiring:
```bash
curl https://ifconfig.me
```
*Natija:* Endi IP manzil WAN2 manziliga o'zgargan bo'lishi kerak!

### 3. Holat Jadvalini Tekshirish (CLI):
```bash
pfctl -ss | grep "192.168.200"
```

---

## 🚨 6. Troubleshooting
* ⚠️ **Muammo: Failover ishlagandan so'ng WAN1 qaytsa ham internet tiklanmayapti.**  
  *Yechim:* `System -> Advanced -> Miscellaneous` bo'limida **State Killing on Gateway Failure** parametrini yoqing. Shunda o'chgan shlyuzdagi barcha qotib qolgan eski sessiyalar tozalanadi.
* ⚠️ **Muammo: Ichki serverlarga yoki pfSense WebGUI ga kirib bo'lmay qoldi.**  
  *Yechim:* PBR qoidasi ichki trafikni ham tashqariga haydab yuborgan. LAN dagi birinchi qoida ichki subnetlar uchun Gateway: `default` ekanini tekshiring.

---

## 🏆 7. Mustaqil Topshiriq
Shunday qoida yozingki, ma'mur kompyuteri (10.10.10.50) internetga faqat tezkor WAN1 orqali chiqsin, qolgan barcha ofis xodimlari esa `GW_LOADBALANCE` orqali ikkala kanaldan teng foydalansin.
"""
}

# ==========================================
# DAY 10: OpenVPN Remote Access
# ==========================================
MODULES[10] = {
    "lecture": """# 📚 [KUN-10] LECTURE: Enterprise OpenVPN Remote Access (Road Warrior), PKI/CA va TLS-Crypt

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Masofaviy xodimlar, dasturchilar va rahbarlar uchun har qanday joydan (uy, aeroport, kafe) korporativ serverlarga xavfsiz shifrlangan ulanish qurish. Korxona PKI infratuzilmasi, TLS-Crypt himoyasi va Multi-WAN sharoitida VPN failover mexanizmini o'rganish.

---

## 🧭 Mundarija
1. [OpenVPN Protokoli va SSL/TLS Arxitekturasi](#1-openvpn-protokoli)
2. [PKI (Public Key Infrastructure): CA, Server va Client Sertifikatlari](#2-pki-arxitekturasi)
3. [Nega UDP 1194 va TLS-Crypt?](#3-tls-crypt-va-port-skanerlashdan-himoya)
4. [Split Tunneling vs Full Tunneling](#4-split-vs-full-tunneling)
5. [Multi-WAN bilan OpenVPN Integratsiyasi](#5-multi-wan-bilan-openvpn)
6. [CARP Klasterida OpenVPN VIP Bog'lanishi](#6-carp-va-openvpn)
7. [Xulosa](#7-xulosa)

---

## 1. OpenVPN Protokoli va SSL/TLS Arxitekturasi

OpenVPN — dunyodagi eng sinovdan o'tgan, o'ta moslashuvchan ochiq kodli VPN protokoli hisoblanadi. U foydalanuvchilarni autentifikatsiya qilish va ma'lumotlarni shifrlash uchun **OpenSSL** kutubxonasiga tayanadi:
* **TUN (Tunnel) Rejimi:** Layer 3 (IP darajasida) ishlaydi. Masofaviy mijozlar uchun eng optimal rejim (Broadcast paketlarni o'tkazmaydi, trafik tejaladi).
* **TAP (Bridge) Rejimi:** Layer 2 (Ethernet darajasida) ishlaydi. Korxona bitta umumiy L2 broadcast domenida ishlashi kerak bo'lgan kamdan-kam holatlarda qo'llaniladi.

---

## 2. PKI (Public Key Infrastructure)

Korporativ xavfsizlikda faqat login/parolga ishonish xavflidir. OpenVPN ikki faktorli kriptografiyadan foydalanadi:
1. **Root Certificate Authority (CA):** Korxonaning bosh sertifikatlash markazi (pfSense ichida yaratiladi).
2. **Server Certificate:** pfSense OpenVPN serverining shaxsini tasdiqlovchi sertifikat.
3. **Client Certificates:** Har bir xodimga alohida shaxsiy sertifikat chiqariladi (`user-ali`, `user-nodir`). Agar xodim ishdan ketsa, uning sertifikati bekor qilinadi (Revocation List - CRL).

---

## 3. Nega UDP 1194 va TLS-Crypt?

* **UDP vs TCP:** Nega VPN TCP ustida qurilmasligi kerak? Chunki agar ichki trafik TCP bo'lsa va VPN ham TCP bo'lsa, paket yo'qolganda "TCP-over-TCP meltdown" effekti yuzaga keladi (ikkala qatlam ham qayta so'rov jo'natib kanalni tiqib qo'yadi). UDP 1194 esa yengil va eng tezkor ishlaydi.
* **TLS-Crypt Kuchi:** An'anaviy OpenVPN serveri UDP port 1194 da tinglab turadi va xakerlar skaner qilganda ochiq portni ko'ra oladi. **TLS-Crypt** yordamida esa hatto dastlabki TLS handshake paketlari ham maxsus simmetrik kalit bilan shifrlanadi. Natijada:
  1. Hujumchilar uchun port mutlaqo yopiq (filtrlanmagan/dead) ko'rinadi.
  2. Port skanerlari va DoS hujumlar pfSense yadrosi darajasidayoq to'xtatiladi.

---

## 4. Split Tunneling vs Full Tunneling

* **Split Tunneling (Tavsiya etiladi):** Xodim VPN ga ulanganda, faqat korporativ tarmoqqa boruvchi paketlar (`10.10.0.0/16`) tunnel orqali o'tadi. YouTube, Instagram va oddiy internet trafigi esa xodimning o'z uy interneti orqali ketadi.
* **Full Tunneling:** Xodimning 100% barcha trafigi ofis orqali filtrlanadi. Bu banklar va davlat tashkilotlarida xodimlarning internet xatti-harakatlarini qat'iy nazorat qilish uchun ishlatiladi.

---

## 5. Multi-WAN bilan OpenVPN Integratsiyasi

Agar korxonada 2 ta provayder bo'lsa, xodimlar asosiy provayder uzilganda ham VPN ga ulana olishi kerak:
1. pfSense da OpenVPN server interfeysi sifatida `Localhost` tanlanishi mumkin yoki ikkala WAN uchun alohida Port Forward qilinadi.
2. Xodimning `.ovpn` konfiguratsiya faylida bir nechta `remote` qatori yoziladi:
```text
remote 203.0.113.5 1194 udp
remote 198.51.100.14 1194 udp
```
OpenVPN mijozi birinchi IP javob bermasa, avtomatik ravishda ikkinchi IP ga ulanadi!

---

## 6. CARP Klasterida OpenVPN VIP Bog'lanishi

Ikkita pfSense (CARP klasteri) mavjud bo'lsa, OpenVPN Server jismoniy WAN IP siga emas, balki **WAN CARP VIP** ga biriktiriladi (`Interface: CARP VIP`). Natijada, agar Master firewall ishdan chiqsa, Backup firewall CARP VIP ni o'ziga oladi va OpenVPN serveri ikkinchi tugunda mijozlar uchun zudlik bilan xizmat ko'rsatishni boshlaydi.
""",

    "lab": """# 🛠️ [KUN-10] LAB: OpenVPN RoadWarrior, PKI va Avtomatlashtirilgan Client Export

**Mavzu:** Korxona xodimlari uchun xavfsiz masofaviy ulanish tizimini noldan qurish  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyaning 30 nafar dasturchisi va buxgalteri masofadan (Remote) ishlamoqda. Dasturchilar serverlarga ulanishi uchun IT bo'limi server portlarini (SSH 22, RDP 3389) internetga to'g'ridan-to'g'ri ochib qo'ygan. Oqibatda serverlar har kuni xakerlik brute-force hujumlariga uchramoqda. Rahbariyat barcha tashqi portlarni darhol yopishni va faqat bitta yuqori darajada shifrlangan OpenVPN shlyuzi orqali 2-faktorli (Sertifikat + Parol) ulanishni joriy qilishni buyurdi.

---

## 🗺️ 2. Topologiya va IP Rejasi

```mermaid
flowchart LR
    REMOTE["Masofaviy Xodim (Uy / Noutbuk)\nIP: DHCP (Internet)"] -->|OpenVPN TLS-Crypt: UDP 1194| WAN["pfSense WAN IP: 192.168.100.2"]
    WAN --> PF["OpenVPN Server\nTunnel Network: 10.201.0.0/24"]
    PF --> LAN["Ofis Tarmog'i: 10.10.10.0/24"]
    PF --> DMZ["Serverlar Tarmog'i: 10.10.20.0/24"]
```

---

## ⚙️ 3. Qadam-baqadam Sozlash

### 1-Qadam: Ichki Sertifikatlash Markazini (CA) Yaratish
1. `System -> Cert. Manager -> CAs` ga kiring.
2. **Add** tugmasini bosing:
   * Descriptive name: `Corp_Internal_CA`
   * Method: `Create an internal Certificate Authority`
   * Key type: `RSA`, Key length: `2048` (yoki ECDSA P-384)
   * Digest Algorithm: `SHA256`
   * Lifetime: `3650` kun
   * Common Name: `Corp Internal Root CA`
3. Save qiling.

### 2-Qadam: Server Sertifikatini Chiqarish
1. `Certificates` yorlig'iga o'ting, **Add** bosing:
   * Method: `Create an internal Certificate`
   * Descriptive name: `OpenVPN_Server_Cert`
   * Certificate authority: `Corp_Internal_CA`
   * Certificate Type: `Server Certificate`
   * Common Name: `vpn.corp.local`
2. Save qiling.

### 3-Qadam: OpenVPN Wizard Orqali Serverni Sozlash
1. `VPN -> OpenVPN -> Wizards` ga kiring.
2. Type of Server: `Local User Access` -> Next.
3. Certificate Authority: `Corp_Internal_CA` -> Next.
4. Server Certificate: `OpenVPN_Server_Cert` -> Next.
5. Server sozlamalari:
   * Interface: `WAN`
   * Protocol: `UDP on IPv4`
   * Local Port: `1194`
   * Description: `Corp Remote VPN`
   * Cryptographic Settings:
     * TLS Audio/Data: `TLS Encryption and Authentication` (TLS-Crypt yoqiladi)
     * Encryption Algorithm: `AES-256-GCM`
     * Auth Digest: `SHA256`
   * Tunnel Network: `10.201.0.0/24`
   * IPv4 Local Network: `10.10.10.0/24, 10.10.20.0/24` (Split-tunnel)
   * Concurrent Connections: `50`
   * DNS Server 1: `10.10.10.1`
6. Firewall Rule Configuration:
   * `Firewall Rule (traffic from clients)` -> Katakchani yoqing.
   * `OpenVPN rule (allow traffic through tunnel)` -> Katakchani yoqing.
7. Finish tugmasini bosing.

### 4-Qadam: Client Export Paketini O'rnatish
1. `System -> Package Manager -> Available Packages` ga kiring.
2. `openvpn-client-export` paketini qidiring va o'rnating.

### 5-Qadam: Foydalanuvchi va Mijoz Sertifikatini Yaratish
1. `System -> User Manager -> Users` ga kiring, **Add** bosing.
2. Username: `devuser1`, Password: `StrongUserPassword123!`.
3. `Certificate` bo'limida: **Click to create a user certificate** katakchasini yoqing.
4. Certificate authority: `Corp_Internal_CA`, Key length: `2048`. Save qiling.

### 6-Qadam: Mijoz Konfiguratsiyasini Yuklab Olish
1. `VPN -> OpenVPN -> Client Export` bo'limiga kiring.
2. Remote Access Server: `Corp Remote VPN` tanlanganini tekshiring.
3. Host Name Resolution: `Interface IP Address` (yoki tashqi FQDN domen).
4. Sahifa pastida `devuser1` foydalanuvchisini toping:
   * Windows uchun: `Most Clients (Inline Configurations)` yoki `Windows Installer`.
   * Android / iOS / macOS uchun: `OpenVPN Connect (.ovpn)` profilini yuklab oling.

---

## 🧪 4. Verifikatsiya va Tekshirish

1. Mijoz kompyuteriga (noutbuk yoki telefon) rasmiy **OpenVPN Connect** dasturini o'rnating va yuklab olingan `.ovpn` faylni import qiling.
2. `Connect` tugmasini bosing va parolni kiriting.
3. **pfSense WebGUI da tekshirish:**
   * `Status -> OpenVPN` sahifasiga kiring.
   * `devuser1` ning ulangan vaqti, haqiqiy IP si, unga berilgan virtual IP (`10.201.0.2`), jo'natilgan va qabul qilingan baytlar ko'rinishi kerak!
4. **Tarmoq aloqasini tekshirish (Mijoz kompyuteridan):**
```bash
ping 10.10.20.80
```
*(DMZ dagi serverga to'g'ridan-to'g'ri aloqa borligini ko'rasiz).*
5. **Split Tunnelni tekshirish:**
```bash
tracert 10.10.20.80
tracert 8.8.8.8
```
*Natija:* Ofis serveriga yo'l 10.201.0.1 orqali, Google ga yo'l esa foydalanuvchining o'z shaxsiy provayderi orqali o'tayotganini tasdiqlang.

---

## 🚨 5. Troubleshooting
* ⚠️ **Muammo: TLS Handshake failed xatosi.**  
  *Yechim:* pfSense va mijoz kompyuterida soat vaqtini (NTP) tekshiring. Agar vaqt 5 minutdan ortiq farq qilsa, TLS sertifikatlari rad etiladi.
* ⚠️ **Muammo: Ulandi, lekin serverlarga ping bormayapti.**  
  *Yechim:* `Firewall -> Rules -> OpenVPN` interfeysida ruxsat beruvchi qoida borligini tekshiring. Shuningdek, ichki serverning o'zida Windows Firewall begona subnetdan (10.201.0.0/24) kelgan pingni bloklamayotganiga ishonch hosil qiling.

---

## 🏆 6. Mustaqil Topshiriq
`Certificate Revocation List (CRL)` yarating va ishdan ketgan sinov foydalanuvchisining sertifikatini bekor qiling. Uning darhol ulanolmay qolishini loglarda tekshiring.
"""
}

# ==========================================
# DAY 11: OpenVPN Site-to-Site & CSO
# ==========================================
MODULES[11] = {
    "lecture": """# 📚 [KUN-11] LECTURE: OpenVPN Site-to-Site Tunneling va Client Specific Overrides (CSO)

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Markaziy Bosh ofis (Headquarters - HQ) bilan viloyatlardagi filiallarni (Branches) yagona shifrlangan tarmoqqa birlashtirish, Client Specific Overrides (CSO) orqali har bir filialga statik subnet yo'naltirish (`iroute`) va marshrutlash mantig'ini chuqur o'rganish.

---

## 🧭 Mundarija
1. [Site-to-Site VPN Arxitekturasi: Peer-to-Peer](#1-site-to-site-arxitekturasi)
2. [Shared Key vs SSL/TLS (PKI) Taqqoslovi](#2-shared-key-vs-ssltls)
3. [Client Specific Overrides (CSO) va `iroute` Mexanizmi](#3-cso-va-iroute)
4. [Hub-and-Spoke vs Mesh Marshrutlash](#4-hub-and-spoke-vs-mesh)
5. [Multi-WAN Ustida Site-to-Site Ishonchliligi](#5-multi-wan-va-site-to-site)
6. [Xulosa](#6-xulosa)

---

## 1. Site-to-Site VPN Arxitekturasi

Site-to-Site VPN ikki yoki undan ortiq butun tarmoq infratuzilmasini o'zaro bog'laydi. Filialdagi oddiy foydalanuvchilar o'z kompyuterlariga hech qanday VPN dastur o'rnatmaydilar — barcha shifrlash va yo'naltirish ishlarini chekka routerlar (pfSense HQ va pfSense Branch) o'z zimmasiga oladi.

```mermaid
flowchart LR
    subgraph HQ["Bosh Ofis (Toshkent HQ)"]
        LAN_HQ["LAN: 10.10.0.0/16"] --- PF_HQ["pfSense HQ\nWAN: 203.0.113.10"]
    end

    subgraph TUNNEL["OpenVPN Tunnel (10.250.0.0/24)"]
        PF_HQ <== "SSL/TLS Shifrlangan Aloqa" ==> PF_BR1["pfSense Samarqand\nWAN: Dinamik/CGNAT"]
        PF_HQ <== "SSL/TLS Shifrlangan Aloqa" ==> PF_BR2["pfSense Buxoro\nWAN: Dinamik/CGNAT"]
    end

    subgraph BR1["Filial 1 (Samarqand)"]
        PF_BR1 --- LAN_BR1["LAN: 10.20.0.0/16"]
    end

    subgraph BR2["Filial 2 (Buxoro)"]
        PF_BR2 --- LAN_BR2["LAN: 10.30.0.0/16"]
    end
```

---

## 2. Shared Key vs SSL/TLS (PKI)

* **Shared Key (Eskirgan usul):** Ikkala routerga bitta umumiy maxfiy kalit fayl yuklanadi. Kamchiliklari: Faqat ikkita nuqta (Point-to-Point) o'rtasida ishlaydi, uchinchi filialni ulab bo'lmaydi va Perfect Forward Secrecy (PFS) ta'minlanmaydi.
* **SSL/TLS (Enterprise standart):** HQ da bitta OpenVPN Server turadi va unga 100 ta filial ulanishi mumkin. Har bir filial o'z sertifikatiga ega bo'ladi.

---

## 3. Client Specific Overrides (CSO) va `iroute` Mexanizmi

Oddiy OpenVPN da mijoz ulanganda unga tunneldan IP beriladi. Ammo server o'sha mijoz routerining orqasida qaysi tarmoq (`10.20.0.0/16`) yotganini qayerdan biladi?
Aynan shu yerda **CSO (Client Specific Overrides)** ishga tushadi:
1. Filial ulanayotganda o'zining Sertifikat Nomini (**Common Name - CN**, masalan `branch-samarkand`) taqdim etadi.
2. pfSense HQ ushbu CN ga mos keluvchi CSO qoidasini topadi.
3. OpenVPN ichki routing jadvaliga quyidagi direktiva kiritiladi:
   ```text
   iroute 10.20.0.0 255.255.0.0
   ```
4. Natijada pfSense yadrosi `10.20.0.0/16` ga boruvchi har qanday paketni aynan `branch-samarkand` mijozining tunneliga buradi.

---

## 4. Hub-and-Spoke vs Mesh

* **Hub-and-Spoke:** Barcha filiallar faqat Bosh ofis (HQ) bilan tunnel quradi. Samarqand Buxoro bilan gaplashmoqchi bo'lsa, paket Samarqand -> Toshkent HQ -> Buxoro yo'nalishida tranzit o'tadi. Sozlash oson va xavfsizlik nazorati markazlashgan.
* **Full Mesh:** Har bir filial boshqa barcha filiallar bilan to'g'ridan-to'g'ri bog'lanadi. Katta tarmoqlarda sozlash o'ta murakkab.

---

## 5. Multi-WAN Ustida Site-to-Site Ishonchliligi

Bosh ofisda Dual-WAN bo'lsa:
* Filial OpenVPN mijoz konfiguratsiyasida Bosh ofisning ikkala provayder IP si ko'rsatiladi.
* Agar Bosh ofisning asosiy provayderi uzilsa, filial 10 soniyada Bosh ofisning ikkinchi IP siga qayta ulanadi va tarmoqlararo aloqa tiklanadi.
""",

    "lab": """# 🛠️ [KUN-11] LAB: OpenVPN Site-to-Site Tunneling va CSO Amaliyoti

**Mavzu:** HQ va Filial o'rtasida to'liq marshrutlangan L3 tunnel qurish  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyaning Toshkentdagi Bosh ofisida yagona 1C ERP va fayl serveri joylashgan. Samarqanddagi yangi ochilgan filial xodimlari ushbu serverga kira olmayapti. Filialda oq IP manzil yo'q (mobil provayder NAT ortida). Shunday tunnel qurish kerakki, filial xodimlari 1C serverga to'g'ridan-to'g'ri `10.10.20.50` lokal IP si orqali ulanishsin va filialdagi IP kameralarni Bosh ofis xavfsizlik xizmati ko'ra olsin.

---

## 🗺️ 2. Topologiya va IP Rejasi

| Lokatsiya | Router Nomi | WAN IP | LAN Subnet | Tunnel IP |
|---|---|---|---|---|
| **Bosh Ofis** | `pfSense-HQ` | `192.168.100.10` (Static) | `10.10.0.0/16` | `10.250.0.1/24` |
| **Filial** | `pfSense-Branch` | DHCP (NAT ortida) | `10.20.0.0/16` | `10.250.0.2/24` |

---

## ⚙️ 3. Qadam-baqadam Sozlash

### 1-Qadam: Bosh Ofisda (HQ) PKI va Sertifikatlarni Tayyorlash
1. `System -> Cert. Manager -> Certificates` ga kiring.
2. Server sertifikatini yarating: `HQ_S2S_Server_Cert` (Type: Server Certificate).
3. Filial uchun alohida mijoz sertifikatini yarating:
   * Common Name: `branch-samarkand` (KRITIK: bu nom CSO da kerak bo'ladi!).
   * Type: User Certificate.

### 2-Qadam: HQ da OpenVPN Serverini Sozlash
1. `VPN -> OpenVPN -> Servers` -> **Add**:
   * Server Mode: `Peer to Peer (SSL/TLS)`
   * Protocol: `UDP on IPv4`, Interface: `WAN`, Port: `1195`
   * Server Certificate: `HQ_S2S_Server_Cert`
   * IPv4 Tunnel Network: `10.250.0.0/24`
   * IPv4 Local Network/s: `10.10.0.0/16`
   * IPv4 Remote Network/s: *Bo'sh qoldiring* (chunki bir nechta filial bo'ladi).
2. Saqlang.

### 3-Qadam: HQ da Client Specific Overrides (CSO) Yaratish
1. `VPN -> OpenVPN -> Client Specific Overrides` yorlig'iga o'ting, **Add** bosing:
   * Common Name: `branch-samarkand` (Mijoz sertifikati bilan 100% bir xil bo'lishi shart!).
   * IPv4 Remote Network/s: `10.20.0.0/16` (Filialning ichki LAN tarmog'i).
2. Saqlang.

### 4-Qadam: Filialda (Branch) Mijozni Sozlash
1. Filial pfSense siga HQ ning `Corp_Internal_CA` Root sertifikatini va `branch-samarkand` mijoz sertifikatini import qiling (`System -> Cert. Manager`).
2. `VPN -> OpenVPN -> Clients` -> **Add**:
   * Server Mode: `Peer to Peer (SSL/TLS)`
   * Server host or address: HQ ning WAN IP si (`192.168.100.10`).
   * Server port: `1195`
   * Client Certificate: `branch-samarkand`
   * IPv4 Tunnel Network: `10.250.0.0/24`
   * IPv4 Remote Network/s: `10.10.0.0/16` (Bosh ofis tarmog'i).
3. Saqlang.

### 5-Qadam: Firewall Qoidalarini Ochish
* Ikkala pfSense da ham `Firewall -> Rules -> OpenVPN` interfeysiga kirib, `Pass Any to Any` qoidasini qo'shing.
* HQ WAN interfeysida UDP port 1195 ga ruxsat bering.

---

## 🧪 4. Verifikatsiya va Sinovlar

1. **Tunnel Holati:**
   * Ikkala routerda ham `Status -> OpenVPN` sahifasiga kiring. Holat yashil **up** bo'lishi va tunnel IP lari (`10.250.0.1` va `10.250.0.2`) ko'rinishi lozim.
2. **Filialdan Bosh Ofisga Ping:**
   Filial LAN kompyuteridan (`10.20.0.50`):
   ```bash
   ping 10.10.20.50
   tracert 10.10.20.50
   ```
   *Paketlar VPN tunnel orqali o'tib Bosh ofis serveriga yetib borishi kerak.*
3. **Bosh Ofisdan Filialga Ping (Ikki Tomonlama Aloqa):**
   Bosh ofis serveridan (`10.10.20.50`):
   ```bash
   ping 10.20.0.50
   ```
   *Agar javob kelsa, demak `iroute` va CSO 100% to'g'ri ishladi!*

---

## 🚨 5. Troubleshooting
* ⚠️ **Muammo: Filialdan HQ ga ping boradi, lekin HQ dan filialga bormayapti.**  
  *Yechim:* Bu eng mashhur xato. HQ da CSO yaratilmagan yoki Common Name maydonidagi nom sertifikat nomi (`branch-samarkand`) bilan mos kelmagan. Shuningdek, HQ Routing jadvalida `netstat -rn` orqali 10.20.0.0/16 yo'nalishi bor-yo'qligini tekshiring.
"""
}

# ==========================================
# DAY 12: WireGuard
# ==========================================
MODULES[12] = {
    "lecture": """# 📚 [KUN-12] LECTURE: WireGuard High-Performance VPN — FreeBSD Kernel Module va Benchmarking

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Eng zamonaviy, tezkor va xavfsiz VPN protokoli — WireGuard ning pfSense 2.7.2 dagi rasmiy yadro moduli (`if_wg`), kriptografik tamoyillari va gigabitli optik kanallarda OpenVPN bilan ishlash unumdorligini solishtirish.

---

## 🧭 Mundarija
1. [WireGuard Inqilobi va Arxitekturasi](#1-wireguard-inqilobi)
2. [Zamonaviy Kriptografik Stek](#2-zamonaviy-kriptografik-stek)
3. [Cryptokey Routing Tamoyili](#3-cryptokey-routing)
4. [FreeBSD Kernel if_wg vs Go Userspace](#4-freebsd-kernel-moduli)
5. [OpenVPN vs WireGuard Benchmark Tahlili](#5-benchmark-tahlili)
6. [Xulosa](#6-xulosa)

---

## 1. WireGuard Inqilobi va Arxitekturasi

WireGuard — Jason A. Donenfeld tomonidan yaratilgan bo'lib, an'anaviy VPN protokollarining (IPsec, OpenVPN) ulkan kod bazasi va sekinligini butkul o'zgartirdi:
* **Kod hajmi:** OpenVPN ~100,000 qatordan ortiq kodga ega, IPsec esa 400,000 qator. WireGuard esa atigi **~4,000 qator kod**. Bu uning xavfsizlik auditini osonlashtiradi va zaifliklar (vulnerabilities) ehtimolini keskin kamaytiradi.
* **Soddalik:** Murakkab kriptografik kelishuvlar (Cipher Negotiation) yo'q. Bir xil va eng xavfsiz zamonaviy algoritmlar qat'iy belgilangan.

---

## 2. Zamonaviy Kriptografik Stek

WireGuard eskirgan RSA va SHA-1 dan mutlaqo voz kechgan:
* **Shifrlash va Autentifikatsiya:** ChaCha20 va Poly1305 (AEAD).
* **Kalit almashinuvi:** Curve25519 (ECDH - Elliptic Curve).
* **Xeshlash:** BLAKE2s.
* **Kalit derivatsiyasi:** HKDF.

---

## 3. Cryptokey Routing Tamoyili

WireGuard har bir Peer (hamkor) ni oddiy marshrut jadvaliga bog'laydi:
* Har bir Peer o'zining **Public Key** si va ruxsat berilgan IP manzillar ro'yxatiga (**AllowedIPs**) ega.
* Agar paket jo'natilayotganda manzil `AllowedIPs` ga to'g'ri kelsa, u o'sha Peerning ochiq kaliti bilan shifrlanadi.
* Begona kalit bilan shifrlangan yoki `AllowedIPs` dan tashqaridagi IP manzildan kelgan paketlar shunchaki e'tiborsiz tashlab yuboriladi (Drop).

---

## 4. FreeBSD Kernel if_wg vs Go Userspace

pfSense 2.7.2 da WireGuard rasmiy FreeBSD yadro drayveri (`if_wg`) sifatida ishlaydi:
* Userspace (Go/Rust) da har bir paket yadro va dastur o'rtasida xotiradan-xotiraga (Context Switch) nusxalanadi, bu esa protsessorni kuchli yuklaydi.
* **Kernel Module (`if_wg`):** Paketlar bevosita yadro ichida shifrlanadi va marshrutlanadi. Natijada 10Gbps gacha bo'lgan tezliklarda minimal CPU yuklamasi ta'minlanadi.

---

## 5. OpenVPN vs WireGuard Benchmark Tahlili

| Ko'rsatkich | OpenVPN (AES-256-GCM) | WireGuard (ChaCha20-Poly1305) | Yutuq |
|---|:---:|:---:|:---:|
| **Ulanish Vaqti (Handshake)** | 3 - 8 soniya | **< 100 millisoniya** | 50x tezroq |
| **O'tkazuvchanlik (1Gbps kanal)**| ~180 - 250 Mbps | **~850 - 950 Mbps** | 4x tezroq |
| **CPU Yuklamasi (Yuklama ostida)**| 85 - 100% | **15 - 25%** | 4x yengilroq |
| **Roaming (Wi-Fi -> LTE)** | Ulanish uziladi (Re-auth) | **Uzluksiz davom etadi** | Choksiz |
""",

    "lab": """# 🛠️ [KUN-12] LAB: WireGuard High-Performance VPN va iperf3 Benchmark Sinovi

**Mavzu:** WireGuard tunnelini sozlash, Peerlarni bog'lash va OpenVPN bilan tezlikni solishtirish  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyada dizaynerlar va video montajchilar katta hajmdagi (5-10 GB) video fayllarni masofadan serverga yuklamoqda. Mavjud OpenVPN tüneli 100 Mbps dan oshmayapti va fayllarni yuklash soatlab vaqt olyapti. Kompaniya rahbariyati optik kanalning to'liq 1 Gbps tezligidan foydalana oladigan zamonaviy WireGuard VPN infratuzilmasini joriy etishni talab qildi.

---

## ⚙️ 2. Qadam-baqadam Sozlash

### 1-Qadam: WireGuard Paketini O'rnatish
1. `System -> Package Manager -> Available Packages` ga kiring.
2. `WireGuard` paketini o'rnating.

### 2-Qadam: WireGuard Tunnelini Yaratish
1. `VPN -> WireGuard -> Tunnels` ga kiring, **Add Tunnel** bosing:
   * Description: `WG_ENTERPRISE`
   * Listen Port: `51820`
   * Interface Keys: **Generate** tugmasini bosing (Public va Private Key yaratiladi).
2. Saqlang va **Apply Changes** qiling.

### 3-Qadam: WireGuard Interfeysini pfSense ga Biriktirish
1. `Interfaces -> Assignments` bo'limiga o'ting.
2. `Available network ports` dan `tun_wg0` ni tanlab, **Add** bosing.
3. Yangi paydo bo'lgan `OPT` interfeysiga kiring:
   * Enable: Yoqing
   * Description: `WIREGUARD`
   * IPv4 Configuration: `Static IPv4`
   * IPv4 Address: `10.200.0.1/24`
4. Saqlang va Apply qiling.

### 4-Qadam: Peer (Mijoz) Qo'shish
1. `VPN -> WireGuard -> Peers` yorlig'iga o'ting, **Add Peer** bosing:
   * Tunnel: `tun_wg0 (WG_ENTERPRISE)`
   * Description: `Engineer_Laptop`
   * Public Key: *(Mijoz noutbukidagi WireGuard yaratgan Public Key)*
   * Allowed IPs: `10.200.0.2/32`
2. Saqlang va Apply qiling.

### 5-Qadam: Mijoz Qurilmasini Sozlash (Windows / macOS / Linux)
Mijozda rasmiy WireGuard ilovasida yangi profil oching:
```ini
[Interface]
PrivateKey = <Mijozning_Shaxsiy_Private_Key>
Address = 10.200.0.2/24
DNS = 10.10.10.1

[Peer]
PublicKey = <pfSense_WireGuard_Public_Key>
Endpoint = <pfSense_WAN_IP>:51820
AllowedIPs = 10.10.0.0/16
PersistentKeepalive = 25
```

### 6-Qadam: Firewall Qoidalarini Ochish
1. `Firewall -> Rules -> WAN`:
   * Action: `Pass`, Protocol: `UDP`, Destination: `WAN address`, Port: `51820`.
2. `Firewall -> Rules -> WIREGUARD`:
   * Action: `Pass`, Protocol: `Any`, Source: `WIREGUARD net`, Destination: `Any`.

---

## 🧪 3. Verifikatsiya va iperf3 Benchmark

1. Mijozda WireGuard da **Activate** tugmasini bosing.
2. `Status -> WireGuard` da qarang: **Latest Handshake** soniyalari ko'rinishi lozim.
3. **CLI da tekshirish:**
```bash
wg show
```
4. **iperf3 orqali tezlikni o'lchash:**
   * pfSense ichki serverida iperf3 serverni yoqing:
   ```bash
   iperf3 -s
   ```
   * Mijoz noutbukidan VPN orqali sinov o'tkazing:
   ```bash
   iperf3 -c 10.10.20.80 -P 4
   ```
5. Natijani OpenVPN tezligi bilan solishtiring (WireGuard tezligi bir necha barobar yuqori chiqishini guvohi bo'lasiz).
"""
}

# ==========================================
# DAY 13: IPsec IKEv2 Enterprise VTI
# ==========================================
MODULES[13] = {
    "lecture": """# 📚 [KUN-13] LECTURE: Enterprise IPsec IKEv2 Site-to-Site va Routed VTI (Virtual Tunnel Interface)

**Kategoriya:** 2-Hafta: Marshrutlash, Multi-WAN va VPN  
**Maqsad:** Korporativ gigantlar, banklar va telekom operatorlari standarti bo'lgan IPsec IKEv2 protokolini, Phase 1 va Phase 2 kripto-to'plamlarini, hamda an'anaviy Policy-based IPsec o'rniga zamonaviy Route-based VTI arxitekturasini o'rganish.

---

## 🧭 Mundarija
1. [IPsec Arxitekturasi va Standartlari](#1-ipsec-arxitekturasi)
2. [IKEv1 vs IKEv2: Nega IKEv2 Sanoat Standarti?](#2-ikev1-vs-ikev2)
3. [Phase 1 (IKE SA) va Phase 2 (Child SA) Jarayoni](#3-phase-1-va-phase-2)
4. [Policy-Based IPsec vs Route-Based VTI](#4-policy-vs-route-based-vti)
5. [VTI ustida BGP/OSPF Dinamik Marshrutlash](#5-vti-ustida-dinamik-marshrutlash)
6. [Xulosa](#6-xulosa)

---

## 1. IPsec Arxitekturasi

IPsec (Internet Protocol Security) — tarmoq qatlamida (Layer 3) ishlovchi eng xavfsiz protokollar to'plamidir.
* **ESP (Encapsulating Security Payload - IP Protocol 50):** Ma'lumotlarni shifrlash va yaxlitligini ta'minlash uchun asosiy protokol.
* **AH (Authentication Header - IP Protocol 51):** Faqat autentifikatsiya beradi, shifrlamaydi (ishlab chiqarishda kam ishlatiladi).
* **UDP 500 (IKE) va UDP 4500 (NAT-Traversal):** Kalitlarni kelishish va NAT ortidagi qurilmalarni ulash portlari.

---

## 2. IKEv1 vs IKEv2

* **IKEv1 (Eskirgan):** Ko'p paket almashinuvi (Main Mode - 6 ta paket), sekin qayta ulanish, NAT bilan ishlashda qiyinchiliklar.
* **IKEv2 (RFC 7296):**
  * Atigi 4 ta paketda tunnelni o'rnatadi.
  * O'rnatilgan **NAT-Traversal (NAT-T)**.
  * **Dead Peer Detection (DPD):** Aloqa uzilganda soniyalarda aniqlash.
  * **MOBIKE:** IP manzil o'zgarganda tunnelni uzmasdan davom ettirish.

---

## 3. Phase 1 (IKE SA) va Phase 2 (Child SA)

1. **Phase 1 (IKE SA):** Ikki router bir-birini taniydi va o'zaro boshqaruv kanalini xavfsiz qiladi:
   * Diffie-Hellman (DH) guruhlari: Group 14 (2048-bit) yoki Group 19/20 (Elliptic Curve).
   * Shifrlash: `AES-256-GCM` yoki `AES-CBC`.
2. **Phase 2 (Child SA):** Haqiqiy foydalanuvchi ma'lumotlarini tashuvchi shifrlangan tunnel:
   * Perfect Forward Secrecy (PFS): Har bir sessiya uchun yangi mustaqil kalitlar generatsiyasi.

---

## 4. Policy-Based IPsec vs Route-Based VTI

* **Policy-Based (An'anaviy):** Shpion qoidalari (SPD) orqali ishlaydi. Tarmoq interfeysi yo'q, `ping` va `traceroute` bilan tekshirish qiyin, dinamik marshrutlash (OSPF/BGP) ulab bo'lmaydi.
* **Route-Based (VTI - Virtual Tunnel Interface):** pfSense da haqiqiy virtual tarmoq kartasi (`ipsecX`) paydo bo'ladi.
  * Unga IP manzil beriladi (masalan `10.254.254.1/30`).
  * Siz oddiy `route add` orqali trafikni tunnelga yo'naltirasiz.
  * VTI ustidan OSPF va BGP protokollarini bemalol yurgizish mumkin!
""",

    "lab": """# 🛠️ [KUN-13] LAB: Enterprise IPsec IKEv2 Routed VTI Tunnelini Sozlash

**Mavzu:** Korxona va Hamkor bank o'rtasida Routed VTI tunnelini qurish  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniya to'lov tizimiga ulanish uchun yirik tijorat banki bilan B2B integratsiya shartnomasini imzoladi. Bank xavfsizlik talablariga ko'ra, aloqa faqat sanoat standarti bo'lgan **IPsec IKEv2** orqali va marshrutlar moslashuvchan bo'lishi uchun **Routed VTI** orqali tashkil etilishi shart. Bank tomoni o'z parametrlari (AES-256-GCM, DH Group 14, Pre-Shared Key) ni taqdim etdi.

---

## 🗺️ 2. Topologiya va IP Rejasi

```mermaid
flowchart LR
    PF_CORP["Kompaniya pfSense\nWAN: 203.0.113.2\nVTI IP: 10.254.254.1/30"] <== "IPsec IKEv2 Routed VTI" ==> PF_BANK["Bank Router\nWAN: 198.51.100.2\nVTI IP: 10.254.254.2/30"]
    PF_CORP --- LAN_CORP["Korporativ Tarmoq: 10.10.0.0/16"]
    PF_BANK --- LAN_BANK["Bank Servislari: 172.20.0.0/16"]
```

---

## ⚙️ 3. Qadam-baqadam Sozlash

### 1-Qadam: Phase 1 (IKE SA) Sozlash
1. `VPN -> IPsec -> Tunnels` ga kiring, **Add P1** bosing:
   * Key Exchange version: `IKEv2`
   * Internet Protocol: `IPv4`, Interface: `WAN`
   * Remote Gateway: `198.51.100.2` (Bank IP si)
   * Authentication Method: `Mutual PSK`
   * Pre-Shared Key: `VerySecretEnterpriseBankKey2026!#`
   * Phase 1 Proposal:
     * Encryption: `AES256-GCM`, Key Length: `128 bits`
     * Hash: `SHA256`
     * DH Group: `14 (2048 bit)`
   * Dead Peer Detection: `Enable DPD` (10s delay, 5 retries).
2. Saqlang.

### 2-Qadam: Phase 2 VTI (Child SA) Sozlash
1. Yaratilgan P1 ostidagi **Add P2** tugmasini bosing:
   * Mode: `Routed (VTI)`
   * Local Network: `10.254.254.1/30`
   * Remote Network: `10.254.254.2/30`
   * Phase 2 Proposal:
     * Protocol: `ESP`
     * Encryption: `AES256-GCM` (128 bits)
     * PFS Key Group: `14 (2048 bit)`
2. Saqlang va **Apply Changes** qiling.

### 3-Qadam: VTI Interfeysini Qabul Qilish va Marshrut Qo'shish
1. `Interfaces -> Assignments` bo'limiga o'ting.
2. `ipsec1` interfeysini tanlab, **Add** bosing.
3. Yangi interfeysga kiring:
   * Enable: Yoqing
   * Description: `VTI_BANK`
   * IPv4 Configuration: `None` (chunki IP P2 da berilgan).
4. `System -> Routing -> Gateways` bo'limida avtomatik `VTI_BANK_GW` (`10.254.254.2`) paydo bo'lganini tasdiqlang.
5. `System -> Routing -> Static Routes` ga kiring, **Add** bosing:
   * Destination Network: `172.20.0.0/16` (Bank tarmog'i)
   * Gateway: `VTI_BANK_GW`

### 4-Qadam: Firewall Qoidalarini Sozlash
1. `Firewall -> Rules -> WAN`: UDP 500, UDP 4500 va IP Protocol 50 (ESP) ga ruxsat bering.
2. `Firewall -> Rules -> IPsec`: Bank trafigiga ruxsat bering.

---

## 🧪 4. Verifikatsiya va CLI Diagnostika

1. **WebGUI da holatni ko'rish:**
   * `Status -> IPsec` sahifasiga kiring.
   * `Overview` da IKE SA va Child SA holati yashil **ESTABLISHED** bo'lishi kerak.
2. **FreeBSD Konsolida strongSwan diagnostikasi:**
```bash
ipsec statusall
```
3. **Marshrut orqali ping yuborish:**
```bash
ping -S 10.10.10.1 172.20.0.10
```
4. **VTI interfeysida trafikni kuzatish:**
```bash
tcpdump -i ipsec1 -n
```
"""
}

# ==========================================
# DAY 19: CARP Part 1
# ==========================================
MODULES[19] = {
    "lecture": """# 📚 [KUN-19] LECTURE: High Availability (CARP) Klasteri — 1-Qism: L2 Sync, Promiscuous Mode, Virtual IPs va Multi-WAN HA

**Kategoriya:** 3-Hafta: Kiberxavfsizlik, UTM, QoS va HA  
**Maqsad:** Korxonada yagona xavfsizlik devori ishdan chiqish xavfini (Single Point of Failure - SPOF) yo'qotish, ikkita pfSense routerini (Master va Backup) klasterga birlashtirish, CARP protokoli, Virtual IP lar va Multi-WAN sharoitida klaster qurish arxitekturasini chuqur o'rganish.

---

## 🧭 Mundarija
1. [Nega CARP? HSRP va VRRP bilan Farqlari](#1-nega-carp)
2. [CARP Virtual IP va Virtual MAC Mexanizmi](#2-virtual-ip-va-mac)
3. [advbase va advskew: Kim Master va Kim Backup?](#3-advbase-va-advskew)
4. [Virtualizatsiyada Eng Katta Tuzoq: Promiscuous Mode va MAC Spoofing](#4-promiscuous-va-mac-spoofing)
5. [Dedicated PFSYNC L2 Havolasi](#5-dedicated-pfsync-havolasi)
6. [CARP Klasterida Multi-WAN Arxitekturasi](#6-carp-va-multi-wan)
7. [Xulosa](#7-xulosa)

---

## 1. Nega CARP? HSRP va VRRP bilan Farqlari

* **Cisco HSRP:** Cisco mulki bo'lgan yopiq protokol.
* **VRRP (RFC 5798):** Standart protokol, ammo uzoq yillar Cisco patentlari tufayli erkin operatsion tizimlarda xavfsiz qo'llanilishi cheklangan.
* **CARP (Common Address Redundancy Protocol):** OpenBSD loyihasi tomonidan kriptografik xavfsiz va patentlardan xoli qilib yaratilgan. U IP Protocol 112 da ishlaydi va har bir e'lon paketini SHA-1 / HMAC parol bilan tasdiqlaydi.

---

## 2. CARP Virtual IP va Virtual MAC Mexanizmi

Klasterdagi ikkita router alohida jismoniy IP larga ega bo'ladi, lekin tarmoqdagi barcha kompyuterlar yagona virtual shlyuz IP manziliga murojaat qiladi:
* **FW-01 (Master):** LAN Real IP: `10.10.10.2`
* **FW-02 (Backup):** LAN Real IP: `10.10.10.3`
* **CARP VIP (Virtual Gateway):** `10.10.10.1`

Har bir CARP Virtual IP o'zining Virtual MAC manzilini hisoblab chiqaradi:
$$\text{MAC} = \text{00:00:5e:00:01:\{\text{VHID}\}}$$
Masalan, VHID = 1 bo'lsa, tarmoq kartasi `00:00:5e:00:01:01` MAC manzilini oladi.

---

## 3. advbase va advskew

Master va Backup holatini boshqaruvchi ikkita parametr mavjud:
* `advbase`: E'lonlar oralig'i (standart: 1 soniya).
* `advskew`: Kechikish koeffitsiyenti (0 dan 254 gacha).
  * **Master Router:** `advskew = 0` (Har 1 soniyada darhol paket jo'natadi).
  * **Backup Router:** `advskew = 100` (Kutadi. Agar 1 soniya + 100/256 soniya davomida Masterdan xabar kelmasa, o'zini MASTER deb e'lon qiladi!).

---

## 4. Virtualizatsiyada Eng Katta Tuzoq: Promiscuous Mode va MAC Spoofing

> [!CAUTION]
> Agar siz pfSense ni Proxmox, VMware ESXi yoki VMware Workstation da klaster qilsangiz, 90% holatda CARP birinchi urinishda ishlamaydi!

**Nega?** Chunki gipervizorning virtual switchlari xavfsizlik vajidan virtual mashinaga unga tegishli bo'lmagan MAC manzilni (`00:00:5e:00:01:XX`) ishlatishga ruxsat bermaydi:
* **VMware ESXi / Workstation da:** Virtual Switch sozlamalarida quyidagi 3 ta parametrni **Accept** qilish SHART:
  1. `Promiscuous Mode: Accept`
  2. `MAC Address Changes: Accept`
  3. `Forged Transmits: Accept`
* **Proxmox VE da:** Linux Bridge o'zi o'tkazadi, lekin Proxmox Firewall moduli o'chirilgan bo'lishi lozim.

---

## 5. Dedicated PFSYNC L2 Havolasi

Ikkita router o'rtasida holat almashinuvi uchun alohida jismoniy port (SYNC) ajratilishi shart:
* Bu port umumiy switchga ulanmaydi! Ikkala server o'rtasida to'g'ridan-to'g'ri kabel orqali bog'lanadi.
* Nega? Chunki `pfsync` paketlari shifrlanmagan bo'ladi va xavfsizlik devorining butun holat jadvalini tashiydi. Uni umumiy tarmoqqa chiqarish xavfsizlikka ziddir.

---

## 6. CARP Klasterida Multi-WAN Arxitekturasi

Agar ikkala routerda ham Dual-WAN (2 ta provayder) bo'lsa, qanday ulanadi?
```mermaid
flowchart TD
    subgraph WAN_SW1["ISP-1 L2 Switch (VLAN 100)"]
        ISP1["Provayder 1"]
    end
    subgraph WAN_SW2["ISP-2 L2 Switch (VLAN 200)"]
        ISP2["Provayder 2"]
    end

    WAN_SW1 -->|igb0: .2| FW1["FW-01 (Master)"]
    WAN_SW1 -->|igb0: .3| FW2["FW-02 (Backup)"]
    CARP_WAN1["CARP VIP ISP1: .1"] -.-> FW1

    WAN_SW2 -->|igb1: .2| FW1
    WAN_SW2 -->|igb1: .3| FW2
    CARP_WAN2["CARP VIP ISP2: .1"] -.-> FW1

    FW1 <== "Dedicated SYNC Port: igb3" ==> FW2
    FW1 -->|igb2: .2| LAN_SW["Ichki LAN Switch"]
    FW2 -->|igb2: .3| LAN_SW
    CARP_LAN["CARP VIP LAN: 10.10.10.1"] -.-> FW1
```
Har bir WAN kanali uchun alohida tashqi L2 switch qo'yiladi va har bir WAN segmentida alohida CARP VIP olinadi!
""",

    "lab": """# 🛠️ [KUN-19] LAB: High Availability CARP Klasterini Sozlash va L2 Sync Amaliyoti

**Mavzu:** Ikkita pfSense o'rtasida CARP VIP, VHID va Promiscuous Mode ni sozlash  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Korxona zavodida ishlab chiqarish liniyalari 24/7 rejimida ishlaydi. Tunda yagona xavfsizlik devori apparati to'xtab qolsa, navbatchi muhandis yetib kelguncha zavod soatlab to'xtaydi va kompaniyaga katta talofat yetkazadi. Talab: Ikkita mustaqil serverdan iborat CARP klasterini qurish, Master server elektrdan uzilsa ham, Backup server avtomatik ravishda boshqaruvni o'ziga olishi kerak.

---

## 🗺️ 2. Topologiya va IP Rejasi

| Qurilma / Rol | LAN Real IP | SYNC Real IP | CARP VIP (LAN) | VHID | advskew |
|---|---|---|---|---|---|
| **FW-01 (Master)** | `10.10.10.2/24` | `192.168.99.1/24` | `10.10.10.1/24` | `1` | `0` |
| **FW-02 (Backup)** | `10.10.10.3/24` | `192.168.99.2/24` | `10.10.10.1/24` | `1` | `100` |

---

## ⚙️ 3. Qadam-baqadam Sozlash

### 1-Qadam: Gipervizorda Promiscuous Mode ni Yoqish (Virtual foydalanuvchilar uchun)
* **VMware Workstation:**
  * Virtual Network Editor ni administrator sifatida oching.
  * `VMnet1` (LAN) va `VMnet2` (SYNC) sozlamalarida MAC spoofing ruxsat berilganini tekshiring.
* **Proxmox VE:**
  * `pve-firewall` ni o'chirib turing yoki Bridge da mac filtering yo'qligiga ishonch hosil qiling.

### 2-Qadam: SYNC Interfeyslarini Sozlash
1. **FW-01 da:**
   * `Interfaces -> Assignments` da uchinchi portni qabul qiling, nomini `SYNC` deb qo'ying.
   * IPv4 Static: `192.168.99.1/24`.
2. **FW-02 da:**
   * Uchinchi portni qabul qiling, nomi: `SYNC`.
   * IPv4 Static: `192.168.99.2/24`.
3. Ikkala routerda ham `Firewall -> Rules -> SYNC` bo'limiga kirib, `Pass Any to Any` qoidasini qo'shing.

### 3-Qadam: FW-01 (Master) da CARP VIP Yaratish
1. `Firewall -> Virtual IPs` ga kiring, **Add** bosing:
   * Type: `CARP`
   * Interface: `LAN`
   * Address: `10.10.10.1 / 24`
   * Virtual Host ID (VHID): `1`
   * CARP Password: `SecretCarpPassword123`
   * Advertising Frequency: Base: `1`, Skew: `0`
2. Saqlang va **Apply Changes** qiling.

### 4-Qadam: FW-02 (Backup) da CARP VIP Yaratish
1. `Firewall -> Virtual IPs` ga kiring, **Add** bosing:
   * Type: `CARP`
   * Interface: `LAN`
   * Address: `10.10.10.1 / 24`
   * Virtual Host ID (VHID): `1` (Master bilan bir xil bo'lishi shart!)
   * CARP Password: `SecretCarpPassword123`
   * Advertising Frequency: Base: `1`, **Skew: `100`** (KRITIK: bu qiymat uni Backup qiladi!).
2. Saqlang va Apply Changes qiling.

---

## 🧪 4. Verifikatsiya va Holatni Tekshirish

1. **WebGUI da Statusni Ko'rish:**
   * FW-01 da: `Status -> CARP` ga kiring. Holat: **MASTER** deb turishi kerak.
   * FW-02 da: `Status -> CARP` ga kiring. Holat: **BACKUP** deb turishi kerak.
2. **FreeBSD Konsolida Tekshirish:**
```bash
ifconfig carp0
```
*FW-01 da `carp: MASTER vhid 1 advbase 1 advskew 0` chiqishi kerak.*
3. **Mijoz Kompyuteridan ARP Manzilni Tekshirish:**
   Mijoz kompyuteridan ping yuboring:
```bash
ping 10.10.10.1
arp -a | findstr 10.10.10.1
```
*Natija:* MAC manzil jismoniy emas, aynan Virtual MAC bo'lishi kerak: `00-00-5e-00-01-01`.

---

## 🚨 5. Troubleshooting
* ⚠️ **Muammo: Split-Brain (Ikkala router ham o'zini MASTER ko'rsatmoqda).**  
  *Yechim:* L2 broadcast/multicast (IP Protocol 112) paketlari bir-biriga yetib bormayapti. VMware da Promiscuous Mode yoqilmagan yoki firewall da CARP protokoli bloklangan.
"""
}

# ==========================================
# DAY 20: CARP Part 2 (pfsync & XML-RPC)
# ==========================================
MODULES[20] = {
    "lecture": """# 📚 [KUN-20] LECTURE: High Availability Klasteri — 2-Qism: pfsync, XML-RPC va Zero-Downtime Failover

**Kategoriya:** 3-Hafta: Kiberxavfsizlik, UTM, QoS va HA  
**Maqsad:** Master va Backup o'rtasida konfiguratsiyani (Firewall rules, Aliases, VPN, DHCP) real vaqtda avtomat ko'chirish (XML-RPC), ochiq ulanishlar sessiyalarini sinxronlash (`pfsync`) va Master server o'chganda 0 soniya uzilish bilan zaxiraga o'tishni ta'minlash.

---

## 🧭 Mundarija
1. [Nega CARP ning O'zi Yetarli Emas?](#1-nega-carp-yetarli-emas)
2. [pfsync Protokoli va State Table Replikatsiyasi](#2-pfsync-protokoli)
3. [XML-RPC Konfiguratsiya Sinxronizatsiyasi](#3-xmlrpc-sinxronizatsiyasi)
4. [Zero-Downtime Failover Mexanizmi](#4-zero-downtime-failover)
5. [Preemption Rejimi va Maintenance Mode](#5-preemption-va-maintenance)
6. [Xulosa](#6-xulosa)

---

## 1. Nega CARP ning O'zi Yetarli Emas?

Oldingi darsda biz CARP VIP ni sozladik. Ammo agar Master o'chib qolsa nima bo'ladi?
1. **Muammo 1:** Backup routerda qoidalar (Firewall rules) yo'q yoki eski bo'lib qoladi.
2. **Muammo 2:** Foydalanuvchilarning barcha aktiv ulanishlari (Zoom qo'ng'iroqlari, yuklanayotgan fayllar, SSH sessiyalar) uzilib ketadi. Chunki stateful firewall da yangi router ulanishning holatini (State Table) bilmaydi va TCP paketlarni tashlab yuboradi!

Ushbu ikki muammoni hal qilish uchun **`pfsync`** va **`XML-RPC`** kerak bo'ladi.

---

## 2. pfsync Protokoli va State Table Replikatsiyasi

`pfsync` — FreeBSD yadrosining protokoli bo'lib (IP Protocol 240), Master routerda har safar yangi TCP/UDP sessiya ochilganda, uning nusxasini L2 orqali ikkinchi routerga replikatsiya qiladi:
* Master da ochilgan sessiya: `Client: 10.10.10.50:54210 -> Web: 142.250.180.206:443 [ESTABLISHED:ESTABLISHED]`.
* `pfsync` ushbu qatorni 1 millisoniyada Backup router xotirasiga yozib qo'yadi.
* Agar Master to'satdan o'chib qolsa, Backup router sessiyani allaqachon biladi va birorta paket uzilmasdan davom etadi!

---

## 3. XML-RPC Konfiguratsiya Sinxronizatsiyasi

Ma'mur barcha o'zgarishlarni (Firewall Rules, Aliases, NAT, Virtual IPs, OpenVPN sozlamalari) faqat **FW-01 (Master)** da bajaradi.
* Master router o'zgarishni saqlagach, shifrlangan XML-RPC (HTTPS orqali) orqali ushbu sozlamalarni **FW-02 (Backup)** ga avtomat nusxalaydi.
* Backup routerda hech qachon qo'lda qoida yozilmaydi!

---

## 4. Preemption va Maintenance Mode

* **Preemption (`net.inet.carp.preempt=1`):** Agar bitta interfeysda (masalan WAN) aloqa uzilsa, barcha boshqa interfeyslar (LAN, DMZ) ham bir vaqtda zaxiraga o'tishini ta'minlaydi.
* **Persistent Maintenance Mode:** Serverda texnik profilaktika o'tkazish kerak bo'lsa, uni bitta tugma bilan vaqtincha zaxiraga o'tkazib, keyin xotirjam yangilash imkoniyati.
""",

    "lab": """# 🛠️ [KUN-20] LAB: pfsync va XML-RPC Sinxronizatsiyasi bilan Zero-Downtime Failover Mashqi

**Mavzu:** Jonli klasterda konfiguratsiyani sinxronlash va Master o'chirilganda 0s uzilish testi  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Rahbariyat Zoom orqali muhim xalqaro investorlar bilan video konferentsiya o'tkazmoqda. Shu vaqtda asosiy firewall apparatida quvvat bloki portlab o'chib qoldi. Tizim shunday sozlangan bo'lishi kerakki, video qo'ng'iroq bir soniyaga ham to'xtamasin va investorlar nosozlik yuz berganini umuman sezmasin (Zero-Downtime).

---

## ⚙️ 2. Qadam-baqadam Sozlash

### 1-Qadam: FW-01 (Master) da High Availability Sync Sozlash
1. `System -> High Avail. Sync` bo'limiga kiring.
2. **State Synchronization Settings (pfsync):**
   * Synchronize States: **Katakchani yoqing**.
   * Synchronize Interface: `SYNC`
   * Synchronize Peer IP: `192.168.99.2` (FW-02 SYNC IP si).
3. **Configuration Synchronization Settings (XMLRPC Sync):**
   * Synchronize Config to IP: `192.168.99.2`
   * Remote System Username: `admin`
   * Remote System Password: *(FW-02 ning admin paroli)*
   * Sinxronlanadigan qismlarni belgilang:
     * [x] Synchronize Firewall Rules
     * [x] Synchronize Firewall Aliases
     * [x] Synchronize NAT
     * [x] Synchronize Virtual IPs
     * [x] Synchronize Certificates
     * [x] Synchronize OpenVPN
4. Saqlang.

### 2-Qadam: FW-02 (Backup) da pfsync ni Yoqish
1. FW-02 da: `System -> High Avail. Sync` ga kiring.
2. Synchronize States: **Katakchani yoqing**.
3. Synchronize Interface: `SYNC`.
4. Synchronize Peer IP: `192.168.99.1` (FW-01 SYNC IP si).
5. **DIQQAT:** XMLRPC Sync bo'limidagi barcha katakchalarni **BO'SH** qoldiring! (Backup router Masterga hech qachon konfiguratsiya yozmasligi kerak). Saqlang.

---

## 🧪 3. Verifikatsiya va Zero-Downtime Sinovi

### 1. XML-RPC Sinovi:
1. FW-01 (Master) da yangi Firewall Alias yarating: Name: `Test_Sync_Alias`, Type: `Host`, IP: `1.2.3.4`. Saqlang va Apply qiling.
2. FW-02 (Backup) ga o'ting va `Firewall -> Aliases` sahifasini yangilang.
*Natija:* `Test_Sync_Alias` 1 soniya ichida FW-02 da avtomatik paydo bo'lishi kerak!

### 2. State Table (Sessiyalar) Sinovi:
1. FW-01 da konsol oching: `pfctl -ss | wc -l`
2. FW-02 da konsol oching: `pfctl -ss | wc -l`
*Natija:* Ikkala routerda ham ochiq sessiyalar soni bir xil bo'lishi lozim!

### 3. Falokat va Zero-Downtime Sinovi (Grand Test):
1. Mijoz kompyuterida uzluksiz ping yoki SSH ulanishini yoqing:
```bash
ping -t 10.10.10.1
```
2. Boshqa terminalda YouTube yoki Zoom qo'ng'irog'ini ishga tushiring.
3. **FW-01 (Master) ning elektrini birdaniga o'chiring (Power Off / Pull plug)!**
4. Mijoz kompyuteridagi ping oynasiga va video qo'ng'iroqqa qarang:
* **Natija:** Bitta ham ping yo'qolmaydi! Video qo'ng'iroq uzilmaydi! FW-02 soniyaning ulushlarida MASTER ga aylanadi va barcha sessiyalarni o'z zimmasiga oladi.
"""
}

# ==========================================
# DAY 21: HAProxy
# ==========================================
MODULES[21] = {
    "lecture": """# 📚 [KUN-21] LECTURE: Enterprise HAProxy Reverse Proxy, SSL Offloading va CARP Integratsiyasi

**Kategoriya:** 3-Hafta: Kiberxavfsizlik, UTM, QoS va HA  
**Maqsad:** Korxonaning web-servislari, API serverlari va portallarini tashqi dunyoga xavfsiz taqdim etish, millionlab so'rovlarni bir nechta backend serverlarga aqlli taqsimlash (Load Balancing), SSL sertifikatlarni markazlashgan holda boshqarish (SSL Offloading) va HAProxy ni CARP klasteri bilan integratsiya qilish.

---

## 🧭 Mundarija
1. [Reverse Proxy Nima va U Nega Kerak?](#1-reverse-proxy-nima)
2. [HAProxy Arxitekturasi: Frontend, Backend va ACLs](#2-haproxy-arxitekturasi)
3. [SSL/TLS Offloading va HTTP/2 Unumdorligi](#3-ssl-offloading)
4. [Yuklamani Taqsimlash Algoritmlari (Load Balancing Algorithms)](#4-algoritmlar)
5. [Salomatlik Tekshiruvlari (Health Checks)](#5-health-checks)
6. [HAProxy va CARP Klasteri Integratsiyasi](#6-haproxy-va-carp)
7. [Xulosa](#7-xulosa)

---

## 1. Reverse Proxy Nima va U Nega Kerak?

An'anaviy port forward qilinganda, bitta tashqi 443 portini faqat bitta ichki serverga yo'naltirish mumkin. Agar kompaniyada 10 ta web-sayt bo'lsa (`crm.firma.uz`, `api.firma.uz`, `portal.firma.uz`), har biriga alohida oq IP sotib olish kerak bo'ladi.
**HAProxy Reverse Proxy:**
* Barcha tashqi so'rovlarni yagona 80/443 portida qabul qiladi.
* HTTP sarlavhasidagi domenni (`Host: crm.firma.uz`) o'qiydi.
* So'rovni tegishli ichki serverga xavfsiz uzatadi.
* Backend serverlarning haqiqiy IP manzillarini tashqi dunyodan yashiradi (Xavfsizlik pardasi).

```mermaid
flowchart LR
    USERS["Tashqi Foydalanuvchilar\n(Internet)"] -->|HTTPS: 443| VIP["CARP Virtual IP: 203.0.113.1"]
    VIP --> HAPROXY["HAProxy Frontend\n(SSL Offloading & ACL)"]
    
    HAPROXY -->|Host: crm.company.uz| BE_CRM["Backend: CRM Cluster\nSRV-01: 10.10.20.11\nSRV-02: 10.10.20.12"]
    HAPROXY -->|Host: api.company.uz| BE_API["Backend: API Cluster\nAPI-01: 10.10.20.21\nAPI-02: 10.10.20.22"]
```

---

## 2. HAProxy Arxitekturasi: Frontend, Backend va ACLs

* **Frontend:** Tashqi dunyodan kelayotgan ulanishlarni tinglaydigan qism (IP, Port, SSL sertifikati).
* **ACL (Access Control Lists):** Aqlli qoidalar:
  * Masalan: `acl is_crm hdr(host) -i crm.company.uz`
  * Masalan: `acl is_api path_beg /api/`
* **Backend:** Serverlar guruhi. ACL mos kelsa, so'rov mos backendga yo'naltiriladi (`use_backend CRM_Cluster if is_crm`).

---

## 3. SSL/TLS Offloading

Og'ir kriptografik hisob-kitoblarni (RSA/ECC kalit almashinuvi, shifrlash) HAProxy o'z zimmasiga oladi. Backend serverlar esa yengil HTTP da ishlaydi. Bu backend serverlar protsessorini 40% gacha bo'shatadi va SSL sertifikatlarni faqat bitta joyda (pfSense da) yangilash kifoya qiladi.

---

## 4. Yuklamani Taqsimlash Algoritmlari

* **Round Robin:** So'rovlarni serverlarga navbatma-navbat beradi (serverlar quvvati bir xil bo'lsa).
* **Least Connections:** Eng kam aktiv sessiyaga ega bo'lgan bo'sh serverga jo'natadi (og'ir SQL so'rovlar uchun ideal).
* **Source IP Hash:** Bitta foydalanuvchini doim bitta serverga bog'lab qo'yadi.

---

## 5. Salomatlik Tekshiruvlari (Health Checks)

HAProxy har 2 soniyada har bir backend serverga HTTP so'rov jo'natadi:
* Agar server `200 OK` qaytarsa, u sog'lom.
* Agar server qulab tushsa yoki `500 Server Error` qaytarsa, HAProxy uni 1 soniya ichida umumiy ro'yxatdan chiqaradi. Mijozlar xatolikni ko'rmaydi, barcha trafik ishchi serverlarga o'tadi.

---

## 6. HAProxy va CARP Klasteri Integratsiyasi

> [!IMPORTANT]
> **Production Qoidasi:** HAProxy Frontend ni hech qachon pfSense ning jismoniy WAN IP siga biriktirmang! Uni **CARP Virtual IP** siga biriktiring. Shunda Master firewall o'chganda, VIP ikkinchi firewallga o'tadi va ikkinchi firewalldagi HAProxy xizmati saytlarni uzluksiz taqdim etishda davom etadi!
""",

    "lab": """# 🛠️ [KUN-21] LAB: HAProxy Reverse Proxy, SSL Offloading va Serverlar Klasterini Sozlash

**Mavzu:** HAProxy orqali Web-klaster qurish, ACL yo'naltirish va jonli Health Check sinovi  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyaning ommaviy savdo saytiga kiruvchi trafik 5 baravarga oshdi. Bitta server ortiq yuklamani ko'tara olmay qulab tushmoqda. Dasturchilar 2 ta yangi server qo'shdi. IT bo'limiga vazifa: Ushbu serverlarni yagona klasterga birlashtirish, yuklamani teng taqsimlash, SSL sertifikatni o'rnatish va agar serverlardan biri ishdan chiqsa, sayt bir lahzaga ham to'xtamasligini ta'minlash.

---

## ⚙️ 2. Qadam-baqadam Sozlash

### 1-Qadam: pfSense WebGUI Portini Bo'shatish
Standart holatda pfSense WebGUI 443 portida o'tiradi. HAProxy ga joy bo'shatish kerak:
1. `System -> Advanced -> Admin Access` ga kiring.
2. TCP Port: `8443` qilib o'zgartiring. Saqlang. (Endi WebGUI: `https://10.10.10.1:8443`).

### 2-Qadam: HAProxy Paketini O'rnatish
1. `System -> Package Manager -> Available Packages` dan `haproxy` paketini o'rnating.
2. `Services -> HAProxy -> Settings` ga kirib, **Enable HAProxy** ni yoqing.

### 3-Qadam: Backend Serverlar Guruhini Yaratish
1. `Services -> HAProxy -> Backend` yorlig'iga o'ting, **Add** bosing:
   * Name: `WEB_CLUSTER_BACKEND`
   * Balance: `roundrobin`
2. **Server list** qismida backend serverlarni qo'shing:
   * Server 1: Name: `SRV01`, Address: `10.10.20.11`, Port: `80`
   * Server 2: Name: `SRV02`, Address: `10.10.20.12`, Port: `80`
3. **Health check method:**
   * Health check: `HTTP`
   * Http check method: `OPTIONS` yoki `GET`
   * Check frequency: `2000` ms (har 2 soniyada).
4. Saqlang.

### 4-Qadam: Frontend Ni Sozlash
1. `Services -> HAProxy -> Frontend` yorlig'iga o'ting, **Add** bosing:
   * Name: `HTTPS_FRONTEND`
   * External address: `WAN address` (yoki CARP VIP bo'lsa CARP VIP tanlanadi).
   * Port: `443`
   * Type: `SSL / HTTPS (offloading)`
   * Default backend: `WEB_CLUSTER_BACKEND`
2. **Certificate:**
   * SSL Offloading uchun sertifikatni tanlang (masalan ACME Let's Encrypt yoki Wildcard).
3. Saqlang va **Apply Changes** qiling.

### 5-Qadam: Firewall Qoidasini Ochish
1. `Firewall -> Rules -> WAN` ga kiring.
2. Action: `Pass`, Protocol: `TCP`, Destination: `WAN address` (yoki CARP VIP), Port: `443`. Saqlang.

---

## 🧪 3. Verifikatsiya va Jonli Sinovlar

1. **HAProxy Statistika Panelini Ko'rish:**
   * `Status -> HAProxy Stats` sahifasiga kiring.
   * `SRV01` va `SRV02` yashil **UP** holatdaligini tasdiqlang.
2. **Yuklama Taqsimoti Sinovi:**
   Terminaldan bir necha marta so'rov yuboring:
```bash
curl -k https://<WAN_IP>/
```
*Natija:* Javob navbatma-navbat birinchi `SRV01` dan, keyin `SRV02` dan keladi.
3. **Avariya (Health Check Failover) Sinovi:**
   * `SRV01` serverida Nginx/Apache xizmatini to'xtating:
   ```bash
   systemctl stop nginx
   ```
   * 2 soniyadan so'ng HAProxy Stats da `SRV01` qizil **DOWN** holatiga o'tadi.
   * Web-saytga kiring: birorta ham xatolik chiqmaydi, barcha foydalanuvchilar avtomat ravishda ishchi `SRV02` ga yo'naltiriladi!
"""
}

def main():
    print("Writing enriched enterprise modules...")
    for day_num, data in MODULES.items():
        day_dir = os.path.join(BASE_DIR, f"day-{day_num:02d}")
        os.makedirs(day_dir, exist_ok=True)
        
        lec_file = os.path.join(day_dir, "lecture.md")
        lab_file = os.path.join(day_dir, "lab.md")
        
        with open(lec_file, "w", encoding="utf-8") as f:
            f.write(data["lecture"])
            
        with open(lab_file, "w", encoding="utf-8") as f:
            f.write(data["lab"])
            
        print(f"Successfully enriched Day-{day_num:02d} (lecture & lab)")

if __name__ == "__main__":
    main()
