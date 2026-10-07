#!/usr/bin/env python3
"""Check-in diario de HoYoLAB (recompensa por iniciar sesion).

Lanzado por el timer genshin-checkin.timer, una vez al dia. Las cookies de
la cuenta vienen de GENSHIN_COOKIES (variable de entorno, cargada por el
unit desde /root/.genshin/credentials.env) y se consiguieron iniciando
sesion a mano una vez en hoyolab.com; esto nunca pide usuario/contrasena.

Si ya se habia reclamado hoy (p.ej. el timer se repite tras un reinicio)
se trata como exito, no como fallo: es justo el resultado que se busca.
"""
import asyncio
import os
import sys

import genshin


async def main() -> int:
    cookies = os.environ.get("GENSHIN_COOKIES", "").strip()
    if not cookies:
        print("falta GENSHIN_COOKIES en el entorno", file=sys.stderr)
        return 1

    client = genshin.Client(cookies=cookies, region=genshin.types.Region.OVERSEAS)
    try:
        reward = await client.claim_daily_reward(game=genshin.types.Game.GENSHIN)
    except genshin.errors.AlreadyClaimed:
        print("ya estaba reclamado hoy")
        return 0
    except genshin.errors.InvalidCookies:
        print("las cookies han caducado: hay que volver a iniciar sesion en hoyolab.com y renovarlas", file=sys.stderr)
        return 1
    except genshin.errors.GenshinException as e:
        print(f"fallo al reclamar: {e}", file=sys.stderr)
        return 1

    print(f"reclamado: {reward.name} x{reward.amount}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
