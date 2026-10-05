# 📚 [KUN-20] LECTURE: High Availability Klasteri — 2-Qism: pfsync, XML-RPC va Zero-Downtime Failover

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
