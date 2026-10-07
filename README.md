# genshin-checkin

Reclama sola, cada día, la recompensa del check-in diario de HoYoLAB
(primogemas/materiales por iniciar sesión en la web). No toca el juego ni
las misiones diarias dentro de él — eso no se puede automatizar sin violar
los términos de servicio de miHoYo, y este proyecto no lo intenta.

Es un script de una sola pieza pensado para correr con un temporizador de
systemd en un servidor propio (VPS, Raspberry Pi, lo que sea con Linux y
Python). Un único login manual al principio; después, nada.

## Cómo funciona

1. `checkin.py` lee las cookies de sesión de HoYoLAB de la variable de
   entorno `GENSHIN_COOKIES`.
2. Llama a [`genshin.py`](https://github.com/seriaati/genshin.py)
   (`Client.claim_daily_reward()`), que es quien habla con la API real.
3. Si ya estaba reclamado hoy (`AlreadyClaimed`), lo cuenta como éxito —
   es el resultado que se busca, no un fallo.
4. Si las cookies han caducado (`InvalidCookies`), lo dice claro por stderr
   en vez de fallar en silencio. Cuando pase, hay que repetir el paso 2 de
   la instalación.

## Por qué cookies y no usuario/contraseña

`genshin.py` sí tiene métodos de login con contraseña
(`login_with_password`, etc.), pero para cuentas HoYoLAB (overseas) ese
flujo pasa por un captcha geetest interactivo — pensado para una sesión de
terminal con navegador a mano, no para un script desatendido. Y
`login_with_qrcode()` sólo vale para cuentas de **Miyoushe** (China), no
para HoYoLAB.

Lo que sí es automatizable sin fricción: coger las cookies de una sesión ya
iniciada a mano (una vez) y reutilizarlas. Por eso el script sólo pide eso.

## Instalación

Requisitos: Python 3.10+ (el proyecto se probó con 3.13).

```bash
git clone https://github.com/pelayodesantiago98-ctrl/genshin-checkin.git
cd genshin-checkin
python3 -m venv venv
./venv/bin/pip install genshin
```

### 1. Conseguir las cookies

`login_with_qrcode()` no sirve para HoYoLAB (overseas) — ver más arriba.
El camino que funciona es sacarlas de una sesión de navegador ya iniciada:

1. Entra en [hoyolab.com](https://www.hoyolab.com) e inicia sesión con tu
   cuenta, normal, como siempre.
2. Clic derecho en la página → **Inspeccionar** (o F12).
3. Pestaña **Network**. Recarga la página (F5).
4. Filtra por **Fetch/XHR** y busca cualquier petición a
   `bbs-api-os.hoyolab.com` (puedes escribir "hoyolab" en el cuadro de
   filtro de texto).
5. Haz clic en una de esas filas → pestaña **Headers** → sección
   **Request Headers** → copia el valor completo de la línea **Cookie:**
   (una cadena larga de `nombre=valor` separados por `;`).

### 2. Guardar las cookies y las credenciales

```bash
mkdir -p /root/.genshin
cat > /root/.genshin/credentials.env <<'EOF'
GENSHIN_COOKIES="pega_aqui_la_cookie_completa"
EOF
chmod 600 /root/.genshin/credentials.env
```

### 3. Probarlo a mano

```bash
GENSHIN_COOKIES="$(grep GENSHIN_COOKIES /root/.genshin/credentials.env | cut -d= -f2-)" \
  ./venv/bin/python checkin.py
```

Debería imprimir algo como `reclamado: Adventurer's Experience x3`, o
`ya estaba reclamado hoy` si ya lo habías hecho desde la web ese día.

### 4. Automatizarlo con systemd

Copia `systemd/genshin-checkin.service` y `systemd/genshin-checkin.timer`
a `/etc/systemd/system/` (ajusta las rutas de `ExecStart` si no clonaste el
repo en `/usr/local/lib/lepayimio/genshin-checkin`), y:

```bash
systemctl daemon-reload
systemctl enable --now genshin-checkin.timer
systemctl list-timers genshin-checkin.timer
```

Por defecto el timer dispara a las 09:05 UTC, con `Persistent=true`: si el
servidor estaba apagado a esa hora, se lanza en cuanto arranca. Cámbialo
editando `OnCalendar=` en el `.timer`.

Para ver si ha ido bien cualquier día:

```bash
journalctl -u genshin-checkin -n 20
```

## Cuando las cookies caduquen

Antes o después pasará — son cookies de sesión, no una clave de API
permanente. El script lo deja escrito en el log (`InvalidCookies`) en vez
de fallar en silencio. Cuando lo veas, repite el paso 1 (sacar cookies
nuevas) y el paso 2 (sobrescribir `GENSHIN_COOKIES`); no hace falta tocar
nada más.


## Licencia

MIT.
