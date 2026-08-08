#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safer Chile - Generador de QR Codes v3.0
=========================================
Genera códigos QR con isotipo central + diseño de caja completo.

Cada caja física lleva:
  - QR con isotipo Safer Chile centrado (para escaneo)
  - Logo "SAFER CHILE" completo al lado (para branding)
  - ID único de carga
  - Instrucciones de uso

Uso:
    python generador_qr_safer.py --cantidad 100 --url-base "https://saferchile.cl/app"
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
from datetime import datetime


def crear_etiqueta_caja(qr_img, id_carga, logo_horizontal_path=None, texto_empresa="SAFER CHILE",
                         ancho_mm=100, alto_mm=60, dpi=300):
    """
    Crea una etiqueta completa para pegar en caja física.

    Layout:
    ┌─────────────────────────────────────────┐
    │  [QR con isotipo]   SAFER CHILE         │
    │                     Control de Cargas   │
    │  ID: BIO-000001    ┌─────────────────┐  │
    │  Escanear para     │  INSTRUCCIONES  │  │
    │  rastrear →        │  1. Escanear QR │  │
    │                    │  2. Seguir flujo│  │
    └─────────────────────────────────────────┘
    """
    # Dimensiones en píxeles
    px_por_mm = dpi / 25.4
    W = int(ancho_mm * px_por_mm)
    H = int(alto_mm * px_por_mm)

    # Colores corporativos Safer Chile
    COLOR_TEAL = (26, 107, 122)
    COLOR_TEAL_LIGHT = (42, 143, 163)
    COLOR_DARK = (13, 74, 85)
    COLOR_ACCENT = (232, 185, 49)

    # Crear canvas
    etiqueta = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(etiqueta)

    # Fondo con gradiente sutil
    for y in range(H):
        ratio = y / H
        r = int(255 - ratio * 8)
        g = int(255 - ratio * 5)
        b = int(255 - ratio * 3)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Borde principal
    draw.rectangle([4, 4, W-5, H-5], outline=COLOR_TEAL, width=4)

    # Barra superior de marca
    draw.rectangle([0, 0, W, int(H*0.12)], fill=COLOR_TEAL)

    # Fuentes
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(H*0.08))
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(H*0.05))
        font_id = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(H*0.07))
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(H*0.04))
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_id = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Texto en barra superior
    draw.text((int(W*0.03), int(H*0.025)), texto_empresa, fill=(255,255,255), font=font_title)
    draw.text((int(W*0.55), int(H*0.035)), "Control de Cargas Biológicas", fill=(255,255,255), font=font_sub)

    # QR (lado izquierdo, ~45% del ancho)
    qr_size = int(min(W, H) * 0.55)
    qr_resized = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = int(W * 0.04)
    qr_y = int(H * 0.18)
    etiqueta.paste(qr_resized, (qr_x, qr_y))

    # Sombra sutil del QR
    draw.rectangle([qr_x-2, qr_y-2, qr_x+qr_size+2, qr_y+qr_size+2], outline=(200,200,200), width=1)

    # Panel derecho: información
    panel_x = qr_x + qr_size + int(W*0.05)
    panel_w = W - panel_x - int(W*0.04)

    # Logo horizontal si existe
    if logo_horizontal_path and os.path.exists(logo_horizontal_path):
        try:
            logo_h = Image.open(logo_horizontal_path).convert("RGBA")
            logo_h_w = int(panel_w * 0.9)
            logo_h_h = int(logo_h_w * logo_h.size[1] / logo_h.size[0])
            if logo_h_h > int(H*0.18):
                logo_h_h = int(H*0.18)
                logo_h_w = int(logo_h_h * logo_h.size[0] / logo_h.size[1])
            logo_h = logo_h.resize((logo_h_w, logo_h_h), Image.LANCZOS)
            etiqueta.paste(logo_h, (panel_x + (panel_w-logo_h_w)//2, int(H*0.18)), logo_h)
        except Exception as e:
            print(f"  ⚠️  No se pudo cargar logo horizontal: {e}")
    else:
        # Texto como logo fallback
        draw.text((panel_x, int(H*0.18)), "SAFER", fill=COLOR_TEAL, font=font_title)
        draw.text((panel_x, int(H*0.28)), "CHILE", fill=COLOR_DARK, font=font_title)

    # ID de carga destacado
    id_y = int(H * 0.42)
    draw.text((panel_x, id_y), "ID DE CARGA:", fill=(100,100,100), font=font_small)
    draw.text((panel_x, id_y + int(H*0.06)), id_carga, fill=COLOR_DARK, font=font_id)

    # Línea separadora
    draw.line([(panel_x, id_y + int(H*0.14)), (panel_x + panel_w, id_y + int(H*0.14))], 
              fill=COLOR_TEAL, width=2)

    # Instrucciones
    inst_y = id_y + int(H*0.17)
    draw.text((panel_x, inst_y), "INSTRUCCIONES:", fill=COLOR_TEAL, font=font_sub)

    instrucciones = [
        "1. Escanear código QR",
        "2. Seguir el flujo en app",
        "3. Verificar datos de carga",
        "",
        "📞 Emergencias: +56 9 XXXX XXXX",
        "🌐 saferchile.cl"
    ]

    for i, linea in enumerate(instrucciones):
        color = (80, 80, 80) if not linea.startswith("📞") and not linea.startswith("🌐") else COLOR_TEAL
        draw.text((panel_x, inst_y + int(H*0.07) + i*int(H*0.055)), linea, fill=color, font=font_small)

    # Barra inferior con color de acento
    draw.rectangle([0, H-int(H*0.06), W, H], fill=COLOR_ACCENT)
    draw.text((int(W*0.03), H-int(H*0.045)), "⚠️ Carga Biológica - Manejar con precaución", 
              fill=(30,30,30), font=font_small)

    return etiqueta


def generar_qr_con_isotipo(codigo_id, url_base, isotipo_path, tamano_logo_ratio=0.22):
    """Genera QR con isotipo Safer Chile centrado."""
    url = f"{url_base}?carga={codigo_id}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

    if isotipo_path and os.path.exists(isotipo_path):
        qr_w, qr_h = qr_img.size
        logo_size = int(min(qr_w, qr_h) * tamano_logo_ratio)

        isotipo = Image.open(isotipo_path).convert('RGBA')
        isotipo = isotipo.resize((logo_size, logo_size), Image.LANCZOS)

        # Fondo blanco circular
        mask_size = logo_size + 24
        mask = Image.new('RGBA', (mask_size, mask_size), (255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, mask_size, mask_size], fill=(255, 255, 255, 255))

        pos_x = (qr_w - mask_size) // 2
        pos_y = (qr_h - mask_size) // 2
        qr_img.paste(mask, (pos_x, pos_y), mask)

        logo_x = (qr_w - logo_size) // 2
        logo_y = (qr_h - logo_size) // 2
        qr_img.paste(isotipo, (logo_x, logo_y), isotipo)

    return qr_img


def generar_banco_safer_chile(cantidad, url_base, isotipo_path, logo_horizontal_path=None,
                               carpeta_salida="qr_safer_chile", prefijo="BIO"):
    """Genera banco completo de QR + etiquetas para cajas."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta_final = os.path.join(carpeta_salida, f"banco_{timestamp}")
    os.makedirs(carpeta_final, exist_ok=True)

    carpetas = {
        'qr_solo': os.path.join(carpeta_final, "01_qr_solo"),
        'etiquetas': os.path.join(carpeta_final, "02_etiquetas_caja"),
        'etiquetas_print': os.path.join(carpeta_final, "03_etiquetas_impresion"),
        'qr_backup': os.path.join(carpeta_final, "04_qr_sin_logo"),
    }
    for c in carpetas.values():
        os.makedirs(c, exist_ok=True)

    resultados = []

    print("=" * 70)
    print("  SAFER CHILE - GENERADOR DE QR v3.0")
    print("  QR con isotipo + Etiquetas para cajas")
    print("=" * 70)
    print(f"  Cantidad:     {cantidad} códigos")
    print(f"  URL Base:     {url_base}")
    print(f"  Prefijo:      {prefijo}")
    print(f"  Isotipo:      {isotipo_path}")
    print(f"  Logo caja:    {logo_horizontal_path or 'Texto fallback'}")
    print(f"  Carpeta:      {carpeta_final}")
    print("=" * 70)
    print()

    for i in range(1, cantidad + 1):
        codigo_id = f"{prefijo}-{i:06d}"

        # 1. QR con isotipo
        qr_con_logo = generar_qr_con_isotipo(codigo_id, url_base, isotipo_path)
        qr_path = os.path.join(carpetas['qr_solo'], f"QR_{codigo_id}.png")
        qr_con_logo.save(qr_path, quality=95)

        # 2. Etiqueta para caja (tamaño estándar)
        etiqueta = crear_etiqueta_caja(
            qr_img=qr_con_logo,
            id_carga=codigo_id,
            logo_horizontal_path=logo_horizontal_path,
            ancho_mm=100,
            alto_mm=60,
            dpi=300
        )
        etiqueta.save(os.path.join(carpetas['etiquetas'], f"ETIQUETA_{codigo_id}.png"), quality=95)

        # 3. Etiqueta alta resolución para impresión profesional
        etiqueta_print = crear_etiqueta_caja(
            qr_img=qr_con_logo,
            id_carga=codigo_id,
            logo_horizontal_path=logo_horizontal_path,
            ancho_mm=100,
            alto_mm=60,
            dpi=600
        )
        etiqueta_print.save(os.path.join(carpetas['etiquetas_print'], f"PRINT_{codigo_id}.png"), quality=95)

        # 4. QR sin logo (backup)
        qr_puro = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_H,
                                 box_size=20, border=4)
        qr_puro.add_data(f"{url_base}?carga={codigo_id}")
        qr_puro.make(fit=True)
        qr_puro.make_image(fill_color="black", back_color="white").save(
            os.path.join(carpetas['qr_backup'], f"BACKUP_{codigo_id}.png"))

        resultados.append({"id": codigo_id, "url": f"{url_base}?carga={codigo_id}",
                          "qr": qr_path, "etiqueta": os.path.join(carpetas['etiquetas'], f"ETIQUETA_{codigo_id}.png")})

        if i % 10 == 0 or i == cantidad:
            print(f"  ✓ Generados {i}/{cantidad}...")

    # Inventario CSV
    csv_path = os.path.join(carpeta_final, "inventario.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("ID_CARGA,URL,QR_SOLO,ETIQUETA_CAJA,ESTADO\n")
        for r in resultados:
            f.write(f"{r['id']},{r['url']},{os.path.basename(r['qr'])},{os.path.basename(r['etiqueta'])},DISPONIBLE\n")

    # Vista previa HTML
    html_path = os.path.join(carpeta_final, "vista_previa.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Safer Chile - Vista Previa QR</title>
<style>
body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5;}}
h1{{text-align:center;color:#1a6b7a;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:20px;}}
.card{{background:white;padding:15px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);text-align:center;}}
.card img{{max-width:100%;border-radius:4px;}}
.id{{font-weight:bold;color:#1a6b7a;margin-top:10px;}}
</style></head>
<body>
<h1>📦 Safer Chile - Etiquetas para Cajas</h1>
<div class="grid">
""")
        for r in resultados[:20]:  # Mostrar primeros 20
            f.write(f"""<div class="card">
<img src="02_etiquetas_caja/{os.path.basename(r['etiqueta'])}" alt="{r['id']}">
<div class="id">{r['id']}</div>
</div>
""")
        if len(resultados) > 20:
            f.write(f"<p style='text-align:center;color:#666;'>... y {len(resultados)-20} más</p>")
        f.write("""</div></body></html>""")

    print()
    print("=" * 70)
    print("  ✅ BANCO GENERADO EXITOSAMENTE")
    print("=" * 70)
    print(f"  📁 Carpeta:           {carpeta_final}")
    print(f"  🎨 QR con isotipo:    {carpetas['qr_solo']}")
    print(f"  🏷️  Etiquetas caja:    {carpetas['etiquetas']}")
    print(f"  🖨️  Etiquetas print:   {carpetas['etiquetas_print']}")
    print(f"  📄 QR backup:         {carpetas['qr_backup']}")
    print(f"  📊 Inventario:        {csv_path}")
    print(f"  🌐 Vista previa:      {html_path}")
    print()
    print("  ESTRUCTURA DE ARCHIVOS:")
    print("    01_qr_solo/         → QR puro con isotipo (para digital)")
    print("    02_etiquetas_caja/  → Etiquetas listas para pegar en cajas")
    print("    03_etiquetas_impresion/ → Alta resolución (600 DPI)")
    print("    04_qr_sin_logo/     → Backup sin marca")
    print("=" * 70)

    return carpeta_final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Safer Chile - Generador de QR con etiquetas para cajas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS:
  # Básico (solo QR con isotipo):
  python generador_qr_safer.py --cantidad 100 --url-base "https://saferchile.cl/app"

  # Con etiquetas completas para cajas:
  python generador_qr_safer.py --cantidad 100 --url-base "https://saferchile.cl/app" \
      --isotipo "isotipo_safer_chile.png" --logo-horizontal "logo_safer_chile.png"

  # Prefijo personalizado:
  python generador_qr_safer.py --cantidad 500 --url-base "https://saferchile.cl/app" \
      --isotipo "isotipo.png" --prefijo "LAB"
        """
    )
    parser.add_argument("--cantidad", type=int, default=50, help="Cantidad de QR (default: 50)")
    parser.add_argument("--url-base", type=str, default="https://saferchile.cl/app", help="URL base")
    parser.add_argument("--isotipo", type=str, default="isotipo_safer_chile_clean.png",
                        help="Ruta al isotipo (PNG transparente) para centro del QR")
    parser.add_argument("--logo-horizontal", type=str, default=None,
                        help="Ruta al logo horizontal para etiqueta de caja")
    parser.add_argument("--prefijo", type=str, default="BIO", help="Prefijo IDs")

    args = parser.parse_args()

    generar_banco_safer_chile(
        cantidad=args.cantidad,
        url_base=args.url_base,
        isotipo_path=args.isotipo,
        logo_horizontal_path=args.logo_horizontal,
        prefijo=args.prefijo
    )
