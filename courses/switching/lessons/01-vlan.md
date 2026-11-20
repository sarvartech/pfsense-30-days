---
title: "VLAN va 802.1Q: bitta switchda bir nechta tarmoq"
duration: 45
lab: vlan-switching
quiz:
  - q: 802.1Q tegi Ethernet kadriga necha bayt qo'shadi?
    options: ["2", "4", "8", "12"]
    answer: 1
    explain: "TPID (0x8100, 2 bayt) + TCI (PCP 3 bit, DEI 1 bit, VID 12 bit) = 4 bayt."
  - q: VLAN ID uchun nechta qiymat ishlatilishi mumkin?
    options: ["256", "1024", "4094", "65535"]
    answer: 2
    explain: "12 bit = 4096; 0 va 4095 band — 1..4094 ishlatiladi."
  - q: Access port va trunk port farqi?
    options:
      - Access — bitta VLAN, tegsiz; trunk — bir nechta VLAN, tegli
      - Access — tegli, trunk — tegsiz
      - Farqi yo'q
      - Trunk faqat routerlarda bo'ladi
    answer: 0
  - q: Ikki xost bir xil subnetda, lekin turli VLAN da. Ular router'siz bir-birini ping qila oladimi?
    options: ["Ha", "Yo'q — VLAN alohida broadcast domen", "Faqat IPv6 da", "Faqat trunk orqali"]
    answer: 1
---

# VLAN va 802.1Q

## 1. Muammo

Bitta switchga buxgalteriya, mehmon Wi-Fi va IP-kameralar ulangan. Hammasi **bitta broadcast domenda** —
bitta ARP storm hammasini yiqitadi, mehmon kameralarni ko'radi. Yechim — **VLAN**: fizik switchni mantiqiy switchlarga bo'lish.

## 2. 802.1Q tegi

```
| Dst MAC | Src MAC | 0x8100 | PCP|DEI|VID(12) | EtherType | Payload | FCS |
                    └──── 4 bayt 802.1Q teg ────┘
```

* **VID** — VLAN raqami (1–4094)
* **PCP** — QoS ustuvorligi (802.1p), masalan VoIP uchun 5

## 3. Port turlari

| Tur | Nechta VLAN | Teg | Qayerda |
|---|---|---|---|
| **Access** | 1 | Tegsiz (untagged) | Kompyuter, printer, kamera |
| **Trunk** | Ko'p | Tegli (tagged) + bitta native | Switch↔switch, switch↔router, hypervisor |

**Native VLAN** — trunk ichida tegsiz o'tadigan VLAN. Xavfsizlik uchun uni ishlatilmaydigan VLAN ga (masalan 999) o'zgartiring.

## 4. Linuxda VLAN

Ikki usul bor:

```bash
# 1) Sub-interfeys (router-on-a-stick, Proxmox, pfSense)
ip link add link eth0 name eth0.10 type vlan id 10

# 2) VLAN-aware bridge (Proxmox "VLAN aware" aynan shu)
ip link add br0 type bridge vlan_filtering 1
bridge vlan add dev eth1 vid 10 pvid untagged
```

## 5. VLAN loyihalash namunasi

| VLAN | Nomi | Subnet | Izoh |
|---|---|---|---|
| 10 | MGMT | 10.10.10.0/24 | Switch, AP, hypervisor boshqaruvi |
| 20 | SERVERS | 10.10.20.0/24 | DMZ/serverlar |
| 30 | USERS | 10.10.30.0/24 | Xodimlar |
| 40 | GUEST | 172.16.40.0/24 | Faqat internet |
| 50 | IOT | 172.16.50.0/24 | Kameralar, izolyatsiya |

VLAN lar orasidagi trafik **router/firewall** orqali o'tadi (pfSense, MikroTik, L3 switch) — u yerda siyosat qo'llanadi.

## 6. Amaliyot

Labda Linux bridge dan haqiqiy 802.1Q switch yasaysiz va bir subnetdagi xostlarni VLAN bilan ajratasiz.
