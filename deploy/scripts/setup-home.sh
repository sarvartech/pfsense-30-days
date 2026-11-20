#!/usr/bin/env bash
# Home server (Proxmox ichidagi alohida Ubuntu 24.04 VM tavsiya etiladi) ni lab-server sifatida tayyorlash.
# Repo /opt/men-tarmoq ga clone qilingan bo'lishi kerak:
#   sudo git clone <repo-url> /opt/men-tarmoq && cd /opt/men-tarmoq
#   sudo VPS_ENDPOINT=<VPS_IP>:51820 VPS_PUBKEY=<VPS_PUBLIC_KEY> ./deploy/scripts/setup-home.sh
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Root sifatida ishga tushiring"; exit 1; }
REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
[[ "$REPO_DIR" == "/opt/men-tarmoq" ]] || { echo "Repo /opt/men-tarmoq da bo'lishi kerak (hozir: $REPO_DIR)"; exit 1; }
HOME_WG_IP=10.99.0.2

echo "==> Paketlar, Docker, containerlab"
apt-get update -qq
apt-get install -y -qq wireguard python3-venv git curl ca-certificates openssl
command -v docker >/dev/null || curl -fsSL https://get.docker.com | sh
command -v containerlab >/dev/null || bash -c "$(curl -sL https://get.containerlab.dev)"

echo "==> WireGuard (VPS ga chiquvchi tunnel — CGNAT/PPPoE uchun ishlaydi)"
install -d -m 700 /etc/wireguard
[[ -f /etc/wireguard/privatekey ]] || (umask 077; wg genkey > /etc/wireguard/privatekey)
wg pubkey < /etc/wireguard/privatekey > /etc/wireguard/publickey
if [[ ! -f /etc/wireguard/wg0.conf ]]; then
  : "${VPS_ENDPOINT:?VPS_ENDPOINT=<ip>:51820 kerak}" "${VPS_PUBKEY:?VPS_PUBKEY kerak}"
  umask 077
  cat > /etc/wireguard/wg0.conf <<CONF
[Interface]
Address = ${HOME_WG_IP}/24
PrivateKey = $(cat /etc/wireguard/privatekey)
MTU = 1412

[Peer]
PublicKey = ${VPS_PUBKEY}
Endpoint = ${VPS_ENDPOINT}
AllowedIPs = 10.99.0.1/32
PersistentKeepalive = 25
CONF
fi
systemctl enable --now wg-quick@wg0
# Reboot da Docker/agent WireGuard dan oldin ko'tarilsa ham 10.99.0.2 ga bind qila olsin
echo "net.ipv4.ip_nonlocal_bind = 1" > /etc/sysctl.d/90-men-tarmoq.conf
sysctl -q --system

echo "==> lab-agent"
python3 -m venv "$REPO_DIR/lab-agent/.venv"
"$REPO_DIR/lab-agent/.venv/bin/pip" install -q -r "$REPO_DIR/lab-agent/requirements.txt"
install -d -m 700 /etc/men-tarmoq /var/lib/men-tarmoq/labs
if [[ ! -f /etc/men-tarmoq/agent.env ]]; then
  cp "$REPO_DIR/lab-agent/agent.env.example" /etc/men-tarmoq/agent.env
  sed -i "s/^AGENT_TOKEN=.*/AGENT_TOKEN=$(openssl rand -hex 32)/" /etc/men-tarmoq/agent.env
  chmod 600 /etc/men-tarmoq/agent.env
fi
docker build -q -t men-tarmoq/term:latest "$REPO_DIR/lab-agent/term"
HOME_WG_IP=$HOME_WG_IP docker compose -f "$REPO_DIR/deploy/home/docker-compose.yml" up -d
install -m 644 "$REPO_DIR/lab-agent/men-tarmoq-agent.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now men-tarmoq-agent

echo "==> Lab imajlarini oldindan yuklash (birinchi lab tez ochilishi uchun)"
for img in $(grep -rhoE 'image: *[^ ]+' "$REPO_DIR/labs" | awk '{print $2}' | sort -u); do
  docker pull -q "$img" || echo "   ogohlantirish: $img yuklanmadi"
done

cat <<MSG

✅ Home lab-server tayyor.
   Home WireGuard public key : $(cat /etc/wireguard/publickey)   ← VPS ga kiriting
   AGENT_TOKEN               : $(grep ^AGENT_TOKEN= /etc/men-tarmoq/agent.env | cut -d= -f2)   ← VPS .env LAB_AGENT_TOKEN
   Tekshirish: ping 10.99.0.1 ; systemctl status men-tarmoq-agent ; journalctl -u men-tarmoq-agent -f
MSG
