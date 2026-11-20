#!/usr/bin/env bash
# VPS ni tayyorlash: Docker, WireGuard (10.99.0.1), ufw, platforma.
# Foydalanish:  sudo ./deploy/scripts/setup-vps.sh
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Root sifatida ishga tushiring: sudo $0"; exit 1; }
REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> Paketlar"
apt-get update -qq
apt-get install -y -qq wireguard ufw curl git ca-certificates
command -v docker >/dev/null || curl -fsSL https://get.docker.com | sh

echo "==> WireGuard kalitlari"
install -d -m 700 /etc/wireguard
[[ -f /etc/wireguard/privatekey ]] || (umask 077; wg genkey > /etc/wireguard/privatekey)
wg pubkey < /etc/wireguard/privatekey > /etc/wireguard/publickey

if [[ ! -f /etc/wireguard/wg0.conf ]]; then
  HOME_PUBKEY="${HOME_PUBKEY:-}"
  if [[ -z "$HOME_PUBKEY" ]]; then
    echo; echo "VPS public key: $(cat /etc/wireguard/publickey)"
    read -r -p "Home server public key (hozir bo'lmasa Enter — keyin qayta ishga tushirasiz): " HOME_PUBKEY
  fi
  if [[ -n "$HOME_PUBKEY" ]]; then
    umask 077
    cat > /etc/wireguard/wg0.conf <<CONF
[Interface]
Address = 10.99.0.1/24
ListenPort = 51820
PrivateKey = $(cat /etc/wireguard/privatekey)

[Peer]
PublicKey = ${HOME_PUBKEY}
AllowedIPs = 10.99.0.2/32
CONF
    systemctl enable --now wg-quick@wg0
  fi
fi

echo "==> Firewall (ufw)"
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow 22/tcp >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw allow 443/udp >/dev/null
ufw allow 51820/udp >/dev/null
ufw --force enable >/dev/null

echo "==> Platforma .env"
ENV_FILE="$REPO_DIR/deploy/vps/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$REPO_DIR/deploy/vps/.env.example" "$ENV_FILE"
  sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$(openssl rand -hex 32)/; s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 16)/" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo "   $ENV_FILE yaratildi — DOMAIN, ACME_EMAIL, ADMIN_EMAILS, LAB_AGENT_TOKEN ni to'ldiring."
fi

cat <<MSG

✅ VPS tayyor.
   VPS WireGuard public key : $(cat /etc/wireguard/publickey)
   Keyingi qadamlar:
     1) nano $ENV_FILE
     2) DNS: DOMAIN uchun A yozuvi → shu VPS IP
     3) cd $REPO_DIR/deploy/vps && docker compose up -d --build
     4) Home server o'rnatilgach:  wg show   (latest handshake ko'rinishi kerak)
MSG
