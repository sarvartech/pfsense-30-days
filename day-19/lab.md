# 🛠️ [KUN-19] LAB: High Availability CARP Klasterini Sozlash va L2 Sync Amaliyoti

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
