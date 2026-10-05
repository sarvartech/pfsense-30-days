# 🛠️ [KUN-08] LAB: Dual ISP Failover va Policy-Based Load Balancing Amaliyoti

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
