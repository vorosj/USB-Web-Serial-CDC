import os

def generate_index_h():
    # Ellenőrizzük, hogy létezik-e az index.img fájl
    if not os.path.isfile('index.img'):
        raise FileNotFoundError("Az 'index.img' fájl nem található a szkript könyvtárában!")

    # index.img beolvasása
    with open('index.img', 'rb') as f:
        img_data = f.read()

    # index.h fájl tartalmának előkészítése
    header_content = []
    header_content.append('#ifndef INDEX_H')
    header_content.append('#define INDEX_H')
    header_content.append('')
    header_content.append('#include <stdint.h>')
    header_content.append('')
    header_content.append('// FAT12 disk image as a byte array')
    header_content.append(f'const uint8_t diskImage[{len(img_data)}] = {{')

    # Bájtok formázása soronként 16 bájttal
    for i in range(0, len(img_data), 16):
        line_bytes = img_data[i:i+16]
        # Bájtok hexadecimális formátumban, 0x előtaggal
        formatted_bytes = ', '.join(f'0x{b:02X}' for b in line_bytes)
        header_content.append(f'    {formatted_bytes}, // Offset: 0x{i:04X}')

    header_content.append('};')
    header_content.append('')
    header_content.append('#endif // INDEX_H')

    # index.h fájlba írás
    with open('index.h', 'w') as f:
        f.write('\n'.join(header_content))

if __name__ == '__main__':
    try:
        generate_index_h()
    except FileNotFoundError as e:
        print(e)