# 🛠️ [KUN-03] LAB: DHCP Server, Static Mappings va pfSense ni Markaziy NTP Server Qilib Sozlash

**Mavzu:** Dinamik IP tarqatish, Static MAC Reservation, DHCP Options va pfSense NTP orqali barcha mijozlar vaqtini majburiy sinxronlash  
**Nazariya:** [Lecture darsini o'qish](lecture.md)

---

## 🎯 1. Real Korxona Muammosi

> **Biznes Muammo:** Kompaniyaning Windows serverlari va xodimlarning kompyuterlarida soat har xil ko'rsatmoqda (ba'zilarida 7 daqiqa farq bor). Oqibatda xodimlar Active Directory domeniga kira olmayapti (Kerberos xatosi), veb-brauzerlar SSL sertifikat xatolarini bermoqda va IT bo'limi kiberhodisalarni tekshirayotganda loglardagi vaqt chalkashib ketgan. Shuningdek, tarmoqdagi fayl server va printerlar har safar qayta yoqilganda yangi IP olib, butun ofis ishini to'xtatmoqda.
> 
> **Vazifa:** pfSense ning o'zida mavjud bo'lgan ichki NTP servisini yoqish, hech qanday qo'shimcha paket o'rnatmasdan turib uni butun tarmoqqa yagona vaqt serveri qilib berish, DHCP orqali xodimlarga avtomat tarqatish va serverlarga qat'iy statik MAC reservation biriktirish.

---

## 🗺️ 2. Topologiya va IP Rejasi

```mermaid
flowchart TD
    INTERNET["Tashqi Internet (NTP Hovuzlari)"] -->|WAN| PFS["pfSense Shlyuz & NTP Server\nLAN IP: 10.10.10.1\nNTP Port: UDP 123"]
    PFS -->|DHCP Option 42: 10.10.10.1| PC1["Admin PC (10.10.10.50)"]
    PFS -->|Static MAC Lease: 10.10.20.20| SRV["Fayl Server (srv-master.corp)"]
    PFS -->|NTP Redirect NAT (UDP 123)| IOT["IoT Kameralar & Noutbuklar"]
```

---

## ⚙️ 3. Qadam-baqadam Amaliy Sozlash

### 1-Qadam: pfSense Ichki NTP Servisini Faollashtirish (Qo'shimcha Paket Shart Emas!)
1. pfSense WebGUI da: `Services -> NTP` ga kiring.
2. **Interface:** `LAN` (yoki barcha ichki interfeyslar: `LAN`, `DMZ`, `Localhost`) ni tanlang.
3. **NTP Time Servers:**
   * Server 1: `0.pfsense.pool.ntp.org`
   * Server 2: `1.pfsense.pool.ntp.org`
   * Server 3: `time.cloudflare.com`
4. **NTP Graphs:** Log va grafiklar uchun katakchani yoqing.
5. Saqlang va **Apply Changes** qiling.

### 2-Qadam: DHCP Serverni Sozlash va Option 42 (NTP) ni Tanitish
1. `Services -> DHCP Server -> LAN` bo'limiga kiring.
2. **Enable:** `Enable DHCP server on LAN interface` katakchasini yoqing.
3. **Subnet:** `10.10.10.0/24`.
4. **Range:** `10.10.10.100` dan `10.10.10.200` gacha (Dinamik mijozlar uchun).
5. **Gateway:** `10.10.10.1`.
6. **DNS Servers:** `10.10.10.1`.
7. **NTP Servers (Kritik Qadam):**
   * Server 1 maydoniga: `10.10.10.1` deb yozing!
   *(Bu parametr barcha mijozlarga DHCP Option 42 orqali pfSense ni vaqt serveri sifatida uzatadi).*
8. Saqlang.

### 3-Qadam: Serverlar uchun DHCP Static Mapping (MAC Reservation)
1. Xuddi shu `Services -> DHCP Server -> LAN` sahifasining eng pastiga tushiring.
2. `DHCP Static Mappings for this Interface` bloki yonidagi **Add** tugmasini bosing:
   * MAC Address: `00:0c:29:ab:cd:ef` (Serveringizning haqiqiy MAC manzili).
   * IP Address: `10.10.10.20` *(Diapazondan tashqarida bo'lishi shart!)*.
   * Hostname: `srv-master`.
   * Description: `Asosiy Korporativ Server`.
3. Saqlang va Apply Changes qiling.

### 4-Qadam: NTP Hijacking (Majburiy Redirect NAT Qoidasi)
Ba'zi qurilmalar DHCP Option 42 ga bo'ysunmay, tashqi internetdagi boshqa NTP serverlarga chiqishga urinadi. Biz barcha UDP 123 so'rovlarini pfSense ga majburlab buramiz:
1. `Firewall -> NAT -> Port Forward` ga kiring, **Add** bosing:
   * Interface: `LAN`
   * Protocol: `UDP`
   * Source: `LAN net`
   * Destination: `Invert Match` [x] -> Destination: `LAN address` (pfSense ning o'zidan boshqa har qanday manzilga ketsa)
   * Destination Port Range: from `123 (NTP)` to `123 (NTP)`
   * Redirect Target IP: `127.0.0.1` (pfSense ning o'zi)
   * Redirect Target Port: `123`
   * Description: `Redirect all outbound NTP to local pfSense NTP`
2. Saqlang va **Apply Changes** qiling.

---

## 🧪 4. Verifikatsiya va Tekshirish (Testing & CLI)

### 1. pfSense ning O'zida NTP Holatini Tekshirish:
pfSense konsolida yoki SSH da quyidagi buyruqni bering:
```bash
ntpq -p
```
*Kutilgan Natija:* Tashqi hovuzlar ro'yxati chiqadi, ularning birining oldida yulduzcha `*` belgisi turishi (faol manba), `offset` 1-2 millisoniyadan kam va `jitter` minimal bo'lishi lozim:
```text
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*time.cloudflare 10.28.12.221     3 u   45   64  377   18.234   +0.142   0.085
```

### 2. Status WebGUI da Ko'rish:
* `Status -> NTP` sahifasiga kiring.
* Status: **Active**, Stratum: **3**, Server Time aniq ko'rinishi kerak.

### 3. Windows Mijozida Vaqtni Tekshirish:
Windows kompyuteringizda PowerShell / CMD ni oching:
```cmd
w32tm /stripchart /computer:10.10.10.1 /samples:3 /dataonly
```
*Natija:* pfSense javob qaytaradi va offset `d: +00.000123s` (millisoniya) bo'lib chiqadi.

### 4. Linux Mijozida Tekshirish:
```bash
sntp 10.10.10.1
# yoki
chronyc sources
```

### 5. DORA Jarayoni va DHCP Option 42 ni Wireshark/tcpdump orqali Tutish:
pfSense konsolida DORA paketlarini kuzating:
```bash
tcpdump -i vtnet1 -n -vvv port 67 or port 68
```
Mijozda `ipconfig /renew` qiling. DHCP ACK paketining ichida `NTP Servers Option 42: 10.10.10.1` parametri o'tganini ko'rasiz!

---

## 🚨 5. Eng Ko'p Uchraydigan Xatolar va Troubleshooting

* ⚠️ **Muammo: pfSense NTP status 'Unreach/Pending' bo'lib turibdi.**  
  *Yechim:* pfSense ning o'zi internetga chiqa olyaptimi? WAN firewall qoidasida yoki Outbound NAT da pfSense ning o'zidan chiquvchi UDP 123 ga ruxsat borligiga ishonch hosil qiling.
* ⚠️ **Muammo: Static DHCP Mapping qo'shganda 'The IP address must not lie within its configured range' xatosi.**  
  *Yechim:* pfSense qoidasi bo'yicha Statik manzil dinamik oraliqdan (masalan 10.10.10.100 - 200) tashqarida bo'lishi shart (masalan `10.10.10.20` yoki `10.10.10.50`).

---

## 🏆 6. Mustaqil Amaliy Topshiriq (Student Challenge)

1. `Services -> DHCP Server` da **DHCP Option 66** (TFTP Server) ga `10.10.10.1` va **DHCP Option 67** (Bootfile Name) ga `pxelinux.0` parametrlarini kiriting.
2. Mijoz kompyuteridan ushbu optionlar qabul qilinganligini Wireshark orqali tekshiring.
