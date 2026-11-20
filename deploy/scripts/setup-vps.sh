#!/usr/bin/env bash
# VPS ni tayyorlash — MAVJUD LOYIHALARGA TEGMAYDIGAN rejimda.
#  * Docker o'rnatilgan bo'lsa — qayta o'rnatmaydi, boshqa konteynerlarga tegmaydi
#  * Firewall siyosatini o'zgartirmaydi (ufw enable / default deny QILMAYDI);
#    ufw faol bo'lsa — faqat WireGuard porti (va caddy rejimida 80/443) uchun ruxsat QO'SHADI
#  * WireGuard alohida "wg-mt" interfeysida (mavjud wg0 ga tegmaydi)
#  * Platformani avtomatik ishga tushirmaydi — oxirida qo'lda buyruq beriladi
#
# Foydalanish:
#   sudo ./deploy/scripts/preflight-vps.sh            # avval tekshiruv (faqat o'qiydi)
#   sudo MODE=proxy ./deploy/scripts/setup-vps.sh      # yoki MODE=caddy
# Ixtiyoriy: WG_PORT=51820  HOME_PUBKEY=<home public key>
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Root sifatida ishga tushiring: sudo $0"; exit 1; }
REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
MODE="${MODE:-}"
WG_IF=wg-mt
WG_PORT="${WG_PORT:-51820}"
WG_DIR=/etc/wireguard/men-tarmoq

port_busy() { ss -Hltnu "( sport = :$1 )" 2>/dev/null | grep -q .; }

if [[ -z "$MODE" ]]; then
  if port_busy 80 || port_busy 443; then MODE=proxy; else MODE=caddy; fi
  echo "==> MODE avtomatik tanlandi: $MODE"
fi
[[ "$MODE" == caddy || "$MODE" == proxy ]] || { echo "MODE=caddy yoki MODE=proxy bo'lishi kerak"; exit 1; }
if [[ "$MODE" == caddy ]] && { port_busy 80 || port_busy 443; }; then
  echo "❌ 80/443 band — MODE=proxy ishlating (boshqa loyihaga xalaqit bermaslik uchun to'xtadim)"; exit 1
fi

echo "==> Paketlar (faqat yetishmayotganlari)"
need=()
command -v wg >/dev/null    || need+=(wireguard-tools)
command -v curl >/dev/null  || need+=(curl)
command -v git >/dev/null   || need+=(git)
command -v openssl >/dev/null || need+=(openssl)
if ((${#need[@]})); then apt-get update -qq && apt-get install -y -qq "${need[@]}"; fi
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sh
else
  echo "   Docker mavjud: $(docker --version) — o'zgartirilmaydi"
fi
docker compose version >/dev/null 2>&1 || { echo "❌ docker compose plugin kerak (apt install docker-compose-plugin)"; exit 1; }

echo "==> WireGuard ($WG_IF, UDP $WG_PORT)"
if ! ip link show "$WG_IF" >/dev/null 2>&1 && port_busy "$WG_PORT"; then
  echo "❌ UDP $WG_PORT band. Boshqa port tanlang: WG_PORT=51821 $0"; exit 1
fi
if ip -4 route | grep -v "dev $WG_IF" | grep -q '10\.99\.0\.'; then
  echo "❌ 10.99.0.0/24 boshqa interfeysda ishlatilmoqda — konfiguratsiyani qo'lda moslang"; exit 1
fi
install -d -m 700 "$WG_DIR"
[[ -f $WG_DIR/privatekey ]] || (umask 077; wg genkey > "$WG_DIR/privatekey")
wg pubkey < "$WG_DIR/privatekey" > "$WG_DIR/publickey"

if [[ ! -f /etc/wireguard/$WG_IF.conf ]]; then
  HOME_PUBKEY="${HOME_PUBKEY:-}"
  if [[ -z "$HOME_PUBKEY" ]]; then
    echo; echo "   VPS public key: $(cat "$WG_DIR/publickey")"
    read -r -p "   Home server public key (hali yo'q bo'lsa Enter — keyin HOME_PUBKEY=... bilan qayta ishga tushirasiz): " HOME_PUBKEY
  fi
  if [[ -n "$HOME_PUBKEY" ]]; then
    (umask 077; cat > "/etc/wireguard/$WG_IF.conf" <<CONF
# Men Tarmoq: VPS <-> home lab server
[Interface]
Address = 10.99.0.1/24
ListenPort = ${WG_PORT}
PrivateKey = $(cat "$WG_DIR/privatekey")

[Peer]
PublicKey = ${HOME_PUBKEY}
AllowedIPs = 10.99.0.2/32
CONF
)
    systemctl enable --now "wg-quick@$WG_IF"
  fi
else
  echo "   /etc/wireguard/$WG_IF.conf mavjud — o'zgartirilmadi"
fi

echo "==> Firewall"
if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
  ufw allow "$WG_PORT/udp" comment 'men-tarmoq wireguard' >/dev/null
  if [[ "$MODE" == caddy ]]; then
    ufw allow 80/tcp comment 'men-tarmoq' >/dev/null
    ufw allow 443/tcp comment 'men-tarmoq' >/dev/null
    ufw allow 443/udp comment 'men-tarmoq' >/dev/null
  fi
  echo "   ufw faol — faqat ruxsat qoidalari qo'shildi (siyosat o'zgarmadi)"
else
  echo "   ufw faol emas — tegilmadi. Provayder (cloud) firewall bo'lsa, UDP $WG_PORT ni oching."
fi

echo "==> Platforma .env"
ENV_FILE="$REPO_DIR/deploy/vps/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$REPO_DIR/deploy/vps/.env.example" "$ENV_FILE"
  sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$(openssl rand -hex 32)/; s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 16)/" "$ENV_FILE"
  if [[ "$MODE" == proxy ]]; then
    sed -i 's|^COMPOSE_FILE=docker-compose.yml:ports.caddy.yml|# &|; s|^# COMPOSE_FILE=docker-compose.yml:ports.proxy.yml|COMPOSE_FILE=docker-compose.yml:ports.proxy.yml|; s|^# SITE_ADDRESS=:80|SITE_ADDRESS=:80|; s|^# PROXY_PORT=8010|PROXY_PORT=8010|' "$ENV_FILE"
  fi
  chmod 600 "$ENV_FILE"
  echo "   $ENV_FILE yaratildi ($MODE rejimi)"
else
  echo "   $ENV_FILE mavjud — o'zgartirilmadi"
fi

cat <<MSG

✅ VPS tayyorlandi ($MODE rejimi). Hech qaysi mavjud konteyner/firewall siyosati o'zgartirilmadi.
   VPS WireGuard public key : $(cat "$WG_DIR/publickey")
   WireGuard endpoint       : <VPS_IP>:${WG_PORT}

   Keyingi qadamlar:
     1) nano $ENV_FILE        # DOMAIN, ACME_EMAIL, ADMIN_EMAILS, (keyinroq) LAB_AGENT_TOKEN
     2) DNS: DOMAIN uchun A yozuvi → shu VPS IP
MSG
if [[ "$MODE" == proxy ]]; then cat <<MSG
     3) Mavjud reverse proxy da DOMAIN → http://127.0.0.1:8010 (Host sarlavhasi va WebSocket saqlansin)
        Namuna: docs/PLATFORM_DEPLOY.md, 3.5-bo'lim
MSG
fi
cat <<MSG
     4) cd $REPO_DIR/deploy/vps && docker compose up -d --build
MSG
