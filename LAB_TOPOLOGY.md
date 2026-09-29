# 🏗️ pfSense Virtualizatsiya Laboratoriyasi: VMware & Proxmox Sozlash Qo'llanmasi

Ushbu hujjatda pfSense xavfsizlik devorini **VMware Workstation Pro** va **Proxmox VE** gipervizorlarida korxona darajasida virtual tarmoqlar (vSwitch, Linux Bridges, VLAN) bilan qanday qilib to'g'ri ko'tarish kerakligi bosqichma-bosqich yoritilgan.

---

## 1. VMware Workstation Pro Topologiyasi

VMware Workstation Pro-da laboratoriya qilish juda qulay, chunki virtual tarmoq muharriri (**Virtual Network Editor**) yordamida izolyatsiyalangan L2 tarmoq segmentlarini osongina hosil qilish mumkin.

### 🌐 VMware Virtual Network Mapping

| Virtual Adapter | Rejim (Type) | Subnet | Vazifasi | Izoh |
|---|---|---|---|---|
| **VMnet0** | Bridged / Physical | Xost LAN bilan bir xil | Tashqi / Mahalliy | Real Wi-Fi yoki LAN kartaga bog'langan |
| **VMnet1** | Host-Only / Private | `192.168.100.0/24` | **WAN 1 (ISP-1)** | pfSense uchun 1-chi Internet provayder simulyatsiyasi |
| **VMnet2** | Host-Only / Private | `192.168.200.0/24` | **WAN 2 (ISP-2)** | Multi-WAN Failover va Load Balancing uchun 2-chi provayder |
| **VMnet3** | Host-Only / Custom | `10.10.0.0/16` | **LAN Trunk (802.1Q)** | pfSense LAN va barcha VLANlar (10, 20, 30, 40, 50) o'tadigan magistral |
| **VMnet4** | Host-Only / Private | `192.168.99.0/24` | **PFSYNC (CARP Interconnect)** | Ikki pfSense (Master va Backup) o'rtasidagi to'g'ridan-to'g'ri aloqa |

> ⚠️ **Muhim Qoida (VMware):**
> Virtual Network Editor orqali `VMnet1`, `VMnet2`, `VMnet3` va `VMnet4` adapterlarida **"Use local DHCP service to distribute IP addresses"** belgisini **O'CHIRIB QO'YING!** Aks holda VMware DHCP pfSense DHCP bilan to'qnashadi.

---

## 2. Proxmox VE Topologiyasi

Proxmox VE — bu ochiq manbali KVM gipervizori bo'lib, ishlab chiqarish (production) muhitiga 100% mos keladi.

### 🌉 Proxmox Linux Bridge va VLAN Konfiguratsiyasi (`/etc/network/interfaces`)

Proxmox VE da VLANlarni boshqarish uchun **VLAN-Aware Linux Bridge** usulidan foydalanish eng toza va professional yondashuv hisoblanadi.

```text
# Proxmox xostida: /etc/network/interfaces fayli namunasi

auto lo
iface lo inet loopback

iface eno1 inet manual
# Jismoniy tarmoq kartasi (Trunk yoki Uplink)

# Boshqaruv va tashqi WAN ko'prigi
auto vmbr0
iface vmbr0 inet static
    address 192.168.1.100/24
    gateway 192.168.1.1
    bridge-ports eno1
    bridge-stp off
    bridge-fd 0

# WAN 1 uchun alohida izolyatsiyalangan ko'prik
auto vmbr1
iface vmbr1 inet manual
    bridge-ports none
    bridge-stp off
    bridge-fd 0
# Izoh: ISP-1 emulyatsiyasi

# WAN 2 uchun alohida ko'prik (Multi-WAN)
auto vmbr2
iface vmbr2 inet manual
    bridge-ports none
    bridge-stp off
    bridge-fd 0
# Izoh: ISP-2 emulyatsiyasi

# Ichki Korporativ LAN (VLAN-Aware!)
auto vmbr10
iface vmbr10 inet manual
    bridge-ports none
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware yes
    bridge-vids 10 20 30 40 50
# Izoh: Ushbu ko'prik barcha 802.1Q teglangan freymlarni o'tkazadi

# CARP va pfsync uchun xususiy klaster tarmog'i
auto vmbr99
iface vmbr99 inet manual
    bridge-ports none
    bridge-stp off
    bridge-fd 0
```

---

## 3. pfSense Virtual Mashinasi Sozlamalari (VM Specs)

Har ikkala gipervizorda quyidagi spetsifikatsiyalarga amal qiling:

### ⚙️ pfSense VM Konfiguratsiyasi:
* **OS Turi:** FreeBSD 64-bit (FreeBSD 14 / 13)
* **vCPU:** 2 vCPU (Suricata yoki Snort ishlatganda 4 vCPU tavsiya etiladi)
* **vRAM:** 2048 MB (2 GB) — bazaviy holatda; pfBlockerNG va IDS/IPS bilan 4096 MB (4 GB)
* **Disk:** 20–30 GB (ZFS tanlanadi: Auto ZFS (stripe), swap = 2G)
* **Network Adapter (NIC Turi):**
  * Proxmox: `VirtIO (paravirtualized)` — eng yuqori tezlik va past CPU yuki.
  * VMware: `VMXNET3` yoki `e1000`.
* **NIC Ulanishlari:**
  1. `NIC 1` -> WAN1 (`VMnet1` yoki `vmbr1`)
  2. `NIC 2` -> WAN2 (`VMnet2` yoki `vmbr2`)
  3. `NIC 3` -> LAN / VLAN Trunk (`VMnet3` yoki `vmbr10`)
  4. `NIC 4` -> CARP Sync (`VMnet4` yoki `vmbr99`)

---

## 4. Laboratoriya Sinov Mashinalari (Test Clients)

Tarmoq to'g'ri ishlayotganini tekshirish uchun kamida 2 ta yengil VM kerak:

1. **Alpine Linux VM (Juda yengil — 128 MB RAM):**
   * Turli VLANlarga (VLAN 10, 30, 40) ulab DHCP, ping, DNS va internet tezligini tekshirish uchun ideal.
2. **Ubuntu Server 22.04 / 24.04 VM (1-2 GB RAM):**
   * VLAN 20 (DMZ) ga joylashtiriladi.
   * Ustida NGINX, iperf3, Telegraf, Syslog serverlari ishlaydi.
   * NAT va Port Forwarding, Reverse Proxy (HAProxy) testlari shu orqali qilinadi.
