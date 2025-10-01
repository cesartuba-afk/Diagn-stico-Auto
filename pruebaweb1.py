# main.py — Entrevista de Arranque (Argentina)
# Servido en Replit con Flask + PyWebIO

from flask import Flask
from pywebio.platform.flask import webio_view
from pywebio import start_server
from pywebio.input import actions, textarea
from pywebio.output import put_markdown, put_html, put_table, put_buttons, clear, toast

# ------------ Estilos ------------
CSS = """
<style>
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
h1, h2 { font-size: 28px; }
.big { font-size: 22px; line-height: 1.45 }
.btn { font-size: 20px; padding: 14px 18px; }
.table td, .table th { font-size: 18px; padding: 8px; }
</style>
"""

# ------------ Helpers ------------
def elegir(pregunta, opciones):
    """Pregunta con botones de opciones (lista de (label, value))."""
    put_markdown(f"<div class='big'>{pregunta}</div>")
    btns = [{'label': lab, 'value': val} for lab, val in opciones]
    return actions(buttons=btns)

# ------------ App de entrevista ------------
def entrevista():
    clear(); put_html(CSS)
    put_markdown("# Entrevista de arranque (orientativa)")
    put_markdown("_Lenguaje local. No reemplaza pruebas de taller._")

    a = {}

    # Panorama inicial
    a['arranque_estado'] = elegir("¿Qué hace al intentar **arrancar**?",
        [("No gira nada", "no_gira"),
         ("Gira el burro", "gira"),
         ("Arranca pero se apaga", "arranca_se_apaga"),
         ("Arranca y queda", "arranca_ok")])

    if a['arranque_estado'] == 'gira':
        a['vel_burro'] = elegir("Sensación del **burro de arranque**:",
            [("Gira normal", "normal"),
             ("Gira **lento** / pesado", "lento"),
             ("Golpetea / solo **clic**", "clic")])
        a['intentos_explosion'] = elegir("¿Hace **intentos de explosión**?",
            [("No intenta", "no"),
             ("Sí, amaga a arrancar", "si")])
        a['olor_nafta'] = elegir("Olor a **nafta** después de insistir:",
            [("Nada", "nada"), ("Leve", "leve"), ("Fuerte (se enchastró)", "fuerte")])

    elif a['arranque_estado'] == 'no_gira':
        a['tablero'] = elegir("Estado del **tablero** al dar contacto:",
            [("Normal", "normal"), ("Muy tenue / baja tensión", "tenue"), ("Parpadea / raro", "raro")])
        a['clic_llave'] = elegir("Al dar a **arranque**, se escucha:",
            [("Nada", "nada"), ("Un **clic**", "clic"), ("Varios clics seguidos", "multi_clic")])
        a['luces'] = elegir("**Luces bajas** con contacto:",
            [("Normales", "normales"), ("Muy **tenues**", "tenues")])

    elif a['arranque_estado'] == 'arranca_se_apaga':
        a['frio_caliente'] = elegir("¿Pasa **en frío**, **en caliente** o siempre?",
            [("Solo en frío", "frio"), ("Solo caliente", "caliente"), ("Siempre", "siempre")])

    # Alimentación / ECU / tablero
    a['bomba_suena'] = elegir("Al dar contacto, la **bomba de nafta** suena 2–3 s:",
        [("Sí", "si"), ("No", "no"), ("No sé / no se escucha", "nose")])
    a['check'] = elegir("Luz de **CHECK ENGINE**:",
        [("Enciende y se apaga", "ok"),
         ("No enciende nunca", "no_prende"),
         ("Queda encendida fija", "queda_fija")])
    a['combustible'] = elegir("Combustible habitual:",
        [("Nafta", "nafta"), ("Nafta + **GNC**", "gnc"), ("Diésel", "diesel")])

    # Batería / cables
    a['edad_bateria'] = elegir("Edad de la **batería**:",
        [("< 1 año", "menor"), ("1–3 años", "media"), ("> 3 años / ni idea", "mayor")])
    a['bornes'] = elegir("Estado de **bornes** y **cables de masa**:",
        [("Limpios y firmes", "ok"), ("**Sulfatados** / flojos", "mal"), ("No revisado", "nose")])

    # Notas
    a['notas'] = textarea("Notas rápidas (opcional)",
                          placeholder="Lluvia, frío, trabajos previos, puente de batería, etc.",
                          rows=4)

    # -------- Orientación --------
    clear(); put_html(CSS); put_markdown("# Resultado orientativo")
    tips = []
    est = a['arranque_estado']

    if est == 'no_gira':
        if a.get('luces') == 'tenues' or a.get('tablero') == 'tenue' or a['edad_bateria'] == 'mayor':
            tips.append("Posible **batería baja** o mal contacto. Medir tensión en reposo y **caída en arranque**.")
        if a.get('clic_llave') in ('clic', 'multi_clic'):
            tips.append("Revisar **relay/automático del burro** y señal de arranque.")
        if a['bornes'] == 'mal':
            tips.append("Limpiar **bornes** y verificar **masa** al block y carrocería.")

    elif est == 'gira':
        if a.get('vel_burro') == 'lento':
            tips.append("**Burro lento**: revisar batería/cables/masa; medir caída de tensión al dar arranque.")
        if a.get('olor_nafta') in ('leve', 'fuerte') and a.get('intentos_explosion') == 'no':
            tips.append("**Mezcla rica / encharcado**: pedal a fondo (corte de inyección) y probar. Verificar inyección.")
        if a['bomba_suena'] == 'no':
            tips.append("No suena **bomba**: chequear fusible/relay/inercia y **presión** de combustible.")
        if a['check'] == 'no_prende':
            tips.append("Sin **CHECK**: revisar **relés principales**, fusibles y **12V a ECU**.")
        if a['check'] == 'queda_fija':
            tips.append("**CHECK fijo**: leer **códigos** primero; puede haber inmovilizador/claves.")

    elif est == 'arranca_se_apaga':
        if a['frio_caliente'] == 'frio':
            tips.append("Solo **en frío**: ECT/IAT fuera de rango, entrada de aire falsa, batería débil en frío.")
        elif a['frio_caliente'] == 'caliente':
            tips.append("Solo **caliente**: sensor CKP intermitente, presión de nafta cayendo, vapores/EVAP.")
        tips.append("Limpiar **cuerpo de aceleración** y chequear **IAC/ISC**.")

    elif est == 'arranca_ok':
        tips.append("Si ahora está bien, replicar condición de falla: **frío/calor/humedad** y **escaneo OBD**.")

    # Cruces generales
    if a['combustible'] == 'gnc':
        tips.append("Con **GNC**, probar **solo a nafta** para descartar conmutación/instalación de gas.")
    if a['bornes'] == 'mal':
        tips.append("**Limpieza de bornes** y apriete; medir caídas de tensión en **masa** y **positivo**.")
    if a['bomba_suena'] == 'nose':
        tips.append("Confirmar si la **bomba** hace cebado 2–3 s; si no, revisar **relay** y alimentación.")

    if not tips:
        tips.append("Sin pista fuerte. Seguir con **escáner**, lectura de **códigos**, prueba de **chispa** y **presión de combustible**, y sincronismo **CKP/CMP**.")

    # Resumen + tips
    tabla = [['Ítem', 'Valor']] + [[k, v] for k, v in a.items()]
    put_table(tabla)
    put_markdown("## Consejos para seguir")
    for t in tips:
        put_markdown(f"- {t}")

    put_buttons([{'label': 'Nueva entrevista', 'value': 'new', 'class': 'btn'}],
                onclick=lambda _: entrevista())
    toast("Orientativo. Usá criterio de taller.", color='info')

# ------------ Servidor Flask + PyWebIO (Replit) ------------
flask_app = Flask(__name__)
flask_app.add_url_rule('/', 'webio_view', webio_view(entrevista),
                       methods=['GET', 'POST', 'OPTIONS'])

if __name__ == "__main__":
    # Replit expone el puerto 8080 por defecto
    flask_app.run(host="0.0.0.0", port=8080)