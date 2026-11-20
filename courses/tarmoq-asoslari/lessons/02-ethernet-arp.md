---
title: Ethernet, MAC va ARP — L2 dan L3 ga ko'prik
duration: 40
lab: linux-basics
quiz:
  - q: MAC manzil necha bitdan iborat?
    options: ["32", "48", "64", "128"]
    answer: 1
  - q: ARP so'rovi (request) qanday yuboriladi?
    options: ["Unicast", "Broadcast (ff:ff:ff:ff:ff:ff)", "Multicast", "Anycast"]
    answer: 1
    explain: Kim bu IP egasi ekanini bilmaganimiz uchun so'rov L2 broadcast bilan hammaga yuboriladi; javob esa unicast.
  - q: Xost boshqa subnetdagi IP ga paket yubormoqchi. ARP orqali kimning MAC manzilini so'raydi?
    options: ["Manzil xostning", "Default gateway (router)ning", "DNS serverning", "Hech kimning"]
    answer: 1
    explain: Boshqa subnetga yo'l doim gateway orqali — shuning uchun L2 da kadr routerga yuboriladi.
  - q: Linuxda ARP jadvalini ko'rsatuvchi zamonaviy buyruq?
    options: ["arp -a", "ip neigh", "ip route", "ss -a"]
    answer: 1
---

# Ethernet, MAC va ARP

## 1. Ethernet kadri

```
| Preamble | Dst MAC (6B) | Src MAC (6B) | EtherType (2B) | Payload 46–1500B | FCS (4B) |
```

* **EtherType** — ichida nima borligini bildiradi: `0x0800` IPv4, `0x86DD` IPv6, `0x0806` ARP, `0x8100` VLAN tegi.
* **MTU 1500** — standart Ethernet payload chegarasi. PPPoE da u **1492** gacha kamayadi (8 bayt PPPoE sarlavhasi) — uydagi PPPoE internetingizda MSS/MTU muammolari shu sababli bo'ladi.

## 2. MAC manzil

48 bit, masalan `52:54:00:ab:cd:ef`. Birinchi 24 bit — **OUI** (ishlab chiqaruvchi). Maxsus manzillar:

* `ff:ff:ff:ff:ff:ff` — broadcast
* birinchi baytning eng kichik biti `1` — multicast (`01:00:5e:...` IPv4 multicast)

## 3. ARP — "Bu IP kimniki?"

```mermaid
sequenceDiagram
  participant H1 as host1 10.0.12.1
  participant SW as L2 segment
  participant H2 as host2 10.0.12.2
  H1->>SW: ARP Request (broadcast) — Who has 10.0.12.2? Tell 10.0.12.1
  SW->>H2: (hammaga tarqatiladi)
  H2-->>H1: ARP Reply (unicast) — 10.0.12.2 is at aa:bb:cc:..
  Note over H1: ARP keshga yoziladi (ip neigh)
  H1->>H2: ICMP Echo Request (endi MAC ma'lum)
```

Holatlar (`ip neigh`): `REACHABLE`, `STALE`, `DELAY`, `PROBE`, `FAILED`, `INCOMPLETE`.

## 4. Gateway mantig'i

Xost paket yuborishdan oldin o'zidan so'raydi: *"manzil mening subnetimdami?"*

* **Ha** → manzilning o'zining MAC ini ARP orqali topadi.
* **Yo'q** → **default gateway** ning MAC ini topadi va kadrni unga yuboradi.

## 5. Xavfsizlik eslatmasi

ARP autentifikatsiyasiz ishlaydi — shuning uchun **ARP spoofing** (soxta javob) mumkin. Himoya: Dynamic ARP Inspection,
statik yozuvlar, 802.1X, segmentatsiya. Bu haqida "Tarmoq xavfsizligi" kursida batafsil.

## 6. Amaliyot

Pastdagi labni ishga tushiring: ikki xostga IP bering, ping qiling va `tcpdump -ni eth1 arp` bilan ARP almashinuvini o'z ko'zingiz bilan ko'ring.
