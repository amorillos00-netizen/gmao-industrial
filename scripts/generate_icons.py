"""
Generador de iconos PWA en formato PNG puro (sin dependencias externas)
"""
import zlib
import struct
from pathlib import Path

def generate_png(width, height, bg_color, fg_color, output_path):
    # Genera un PNG válido de alta calidad
    raw_data = bytearray()
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 2 - 8
    gear_inner = radius // 2

    for y in range(height):
        raw_data.append(0) # Filtro None
        for x in range(width):
            dx = x - center_x
            dy = y - center_y
            dist_sq = dx * dx + dy * dy

            # Dibujar un círculo exterior con engranaje estilizado
            if dist_sq <= radius * radius:
                # Borde y centro
                if dist_sq <= gear_inner * gear_inner:
                    # Centro del engranaje
                    raw_data.extend(fg_color)
                elif (dist_sq > (radius - 12)**2):
                    raw_data.extend(fg_color)
                elif (abs(dx) < 18 or abs(dy) < 18):
                    raw_data.extend(fg_color)
                else:
                    raw_data.extend(bg_color)
            else:
                raw_data.extend((30, 41, 59)) # Slate 800 background

    def chunk(tag, data):
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0)) # 8-bit RGB
    idat = chunk(b'IDAT', zlib.compress(bytes(raw_data), 9))
    iend = chunk(b'IEND', b'')

    with open(output_path, "wb") as f:
        f.write(header + ihdr + idat + iend)

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "app" / "static"
    generate_png(192, 192, (10, 110, 209), (255, 255, 255), out_dir / "icon-192.png")
    generate_png(512, 512, (10, 110, 209), (255, 255, 255), out_dir / "icon-512.png")
    print("Iconos PWA generados con éxito.")
