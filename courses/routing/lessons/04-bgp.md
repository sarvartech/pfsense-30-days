---
title: "BGP: Internetning marshrutlash protokoli"
duration: 60
lab: bgp-basic
quiz:
  - q: BGP qaysi transportni ishlatadi?
    options: ["UDP 179", "TCP 179", "IP 89", "TCP 443"]
    answer: 1
  - q: eBGP va iBGP farqi?
    options:
      - eBGP — turli AS lar orasida, iBGP — bitta AS ichida
      - eBGP shifrlangan, iBGP yo'q
      - eBGP IPv6 uchun
      - Farqi yo'q
    answer: 0
  - q: BGP da halqa (loop) ning oldini olishning asosiy mexanizmi?
    options: ["TTL", "AS_PATH — o'z AS raqamini ko'rgan router marshrutni rad etadi", "Split horizon", "Hold timer"]
    answer: 1
  - q: Sessiya "Active" holatida qotib qolgan. Eng ehtimolli sabab?
    options: ["Hammasi yaxshi", "TCP 179 ulanishi o'rnatilmayapti (IP/marshrut/ACL/noto'g'ri neighbor manzili)", "Prefiks ko'p", "MTU katta"]
    answer: 1
---

# BGP — Internetning marshrutlash protokoli

## 1. Avtonom tizimlar (AS)

Internet — 75 000+ mustaqil tarmoqlar (AS) to'plami. Har biri o'z **ASN** iga ega (masalan Uztelecom, Beeline, Google — AS15169).
**BGP** (Border Gateway Protocol) — AS lar o'rtasida "qaysi IP bloklarga men orqali yetish mumkin" degan ma'lumotni almashadi.

## 2. Asosiy tushunchalar

* **Path-vector** protokol: har bir marshrut bilan butun **AS_PATH** yuboriladi (`65002 3356 15169`).
* **TCP 179** ustida ishlaydi — ishonchli, lekin sekin konvergensiya.
* **eBGP** (turli AS) — odatda to'g'ridan-to'g'ri ulangan, TTL=1. **iBGP** (bir AS ichida) — full-mesh yoki route reflector.

## 3. Sessiya holatlari

`Idle → Connect → Active → OpenSent → OpenConfirm → Established`

## 4. Eng yaxshi yo'lni tanlash (soddalashtirilgan)

1. Eng yuqori **Weight** (Cisco/FRR lokal)
2. Eng yuqori **LOCAL_PREF** (AS ichida chiqish nuqtasini tanlash)
3. Lokal yaratilgan marshrut
4. Eng qisqa **AS_PATH**
5. Eng past **ORIGIN** (IGP < EGP < incomplete)
6. Eng past **MED** (qo'shni AS ga kirish nuqtasini taklif qilish)
7. eBGP > iBGP
8. IGP bo'yicha eng yaqin next-hop … va hokazo

## 5. FRR konfiguratsiyasi

```
router bgp 65001
 bgp router-id 192.0.2.1
 neighbor 172.16.0.2 remote-as 65002
 address-family ipv4 unicast
  network 10.1.0.0/24
  neighbor 172.16.0.2 prefix-list OUT-OWN out
 exit-address-family
!
ip prefix-list OUT-OWN seq 10 permit 10.1.0.0/24
```

> ⚠️ **Production qoidasi:** eBGP qo'shniga hech qachon filtrsiz e'lon qilmang. 2008-yilda Pakistan Telecom
> YouTube prefiksini noto'g'ri e'lon qilib, butun dunyo bo'ylab YouTube ni o'chirib qo'ygan. RPKI va prefix-list — majburiy.

## 6. Diagnostika

```
show bgp summary
show bgp ipv4 unicast
show bgp ipv4 unicast neighbors 172.16.0.2 advertised-routes
show bgp ipv4 unicast neighbors 172.16.0.2 routes
```

## 7. Amaliyot

Labda ikki AS ni eBGP bilan ulab, mijoz tarmoqlarini e'lon qilasiz va pc1 ↔ pc2 bog'lanishini ta'minlaysiz.
