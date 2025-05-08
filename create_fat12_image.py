import struct
import os
import time
import math

def create_fat12_image():
    # FAT12 alap paraméterek
    sector_size = 512
    sectors_per_cluster = 1
    reserved_sectors = 1
    fat_copies = 2
    root_dir_entries = 16  # Csökkentve, mert csak 1 fájlunk van
    sectors_per_track = 18
    heads = 2

    # Ellenőrizzük, hogy létezik-e az index.html fájl
    if not os.path.isfile('index.html'):
        raise FileNotFoundError("Az 'index.html' fájl nem található a szkript könyvtárában!")

    # index.html tartalom beolvasása
    with open('index.html', 'rb') as f:
        html_content = f.read()
    html_size = len(html_content)
    html_sectors = (html_size + sector_size - 1) // sector_size

    # Gyökérkönyvtár szektorok száma
    root_dir_sectors = (root_dir_entries * 32 + sector_size - 1) // sector_size

    # Adat terület klaszter számainak becslése (minimum 2 klaszter az index.html-nek)
    data_clusters = max(2, html_sectors)

    # FAT tábla méretének kiszámítása
    # Egy FAT12 bejegyzés 12 bit (1.5 bájt), 2 klaszter 3 bájt
    fat_entries_needed = data_clusters + 2  # +2 a fenntartott klaszterek miatt
    fat_bytes_needed = fat_entries_needed * 3 // 2
    sectors_per_fat = (fat_bytes_needed + sector_size - 1) // sector_size
    sectors_per_fat = max(1, sectors_per_fat)  # Legalább 1 szektor

    # Teljes szektorszám kiszámítása
    total_sectors = (
        reserved_sectors +  # Boot szektor
        fat_copies * sectors_per_fat +  # FAT táblák
        root_dir_sectors +  # Gyökérkönyvtár
        html_sectors  # Adat terület
    )

    # Boot szektor létrehozása
    boot_sector = bytearray(sector_size)
    boot_sector[0:3] = b'\xEB\x3C\x90'  # Ugrás utasítás
    boot_sector[3:11] = b'MSDOS5.0'     # OEM név
    struct.pack_into('<H', boot_sector, 11, sector_size)  # Bájtok per szektor
    boot_sector[13] = sectors_per_cluster  # Szektorok per klaszter
    struct.pack_into('<H', boot_sector, 14, reserved_sectors)  # Fenntartott szektorok
    boot_sector[16] = fat_copies  # FAT másolatok száma
    struct.pack_into('<H', boot_sector, 17, root_dir_entries)  # Gyökérkönyvtár bejegyzések
    struct.pack_into('<H', boot_sector, 19, total_sectors)  # Összes szektor
    boot_sector[21] = 0xF0  # Média típus
    struct.pack_into('<H', boot_sector, 22, sectors_per_fat)  # Szektorok per FAT
    struct.pack_into('<H', boot_sector, 24, sectors_per_track)  # Szektorok per sáv
    struct.pack_into('<H', boot_sector, 26, heads)  # Fejek száma
    struct.pack_into('<I', boot_sector, 28, 0)  # Rejtett szektorok
    struct.pack_into('<I', boot_sector, 32, total_sectors)  # Nagy teljes szektor szám
    boot_sector[36] = 0x00  # Meghajtó száma
    boot_sector[38] = 0x29  # Kiterjesztett boot aláírás
    struct.pack_into('<I', boot_sector, 39, 0x12345678)  # Kötet sorozatszám
    boot_sector[43:54] = b'NO NAME    '  # Kötet címke
    boot_sector[54:62] = b'FAT12   '    # Fájlrendszer típus
    boot_sector[510:512] = b'\x55\xAA'  # Boot szektor aláírás

    # FAT táblák inicializálása
    fat = bytearray(sectors_per_fat * sector_size)
    fat[0:3] = b'\xF0\xFF\xFF'  # Média típus és fenntartott klaszterek

    # FAT tábla frissítése az index.html számára (2. klasztertől kezdve)
    for i in range(html_sectors):
        cluster = 2 + i
        if i == html_sectors - 1:
            value = 0xFFF  # EOF
        else:
            value = cluster + 1  # Következő klaszter
        offset = cluster * 3 // 2
        if cluster % 2 == 0:
            fat[offset] = value & 0xFF
            fat[offset + 1] = ((value >> 8) & 0x0F) | (fat[offset + 1] & 0xF0)
        else:
            fat[offset] = (fat[offset] & 0x0F) | ((value & 0x0F) << 4)
            fat[offset + 1] = (value >> 4) & 0xFF

    # Gyökérkönyvtár bejegyzés az index.html számára
    root_dir = bytearray(root_dir_entries * 32)
    filename = b'INDEX   HTM'  # 8.3 formátum
    root_dir[0:11] = filename
    root_dir[11] = 0x20  # Fájl attribútum (archív)
    # Időbélyegző hozzáadása
    current_time = time.localtime()
    fat_date = ((current_time.tm_year - 1980) << 9) | (current_time.tm_mon << 5) | current_time.tm_mday
    fat_time = (current_time.tm_hour << 11) | (current_time.tm_min << 5) | (current_time.tm_sec // 2)
    struct.pack_into('<H', root_dir, 22, fat_time)  # Létrehozási idő
    struct.pack_into('<H', root_dir, 24, fat_date)  # Létrehozási dátum
    struct.pack_into('<H', root_dir, 26, 2)  # Első klaszter (2)
    struct.pack_into('<I', root_dir, 28, html_size)  # Fájl méret

    # Adat terület előkészítése
    data_area_size = html_sectors * sector_size
    data_area = bytearray(data_area_size)
    data_area[0:html_size] = html_content  # index.html tartalom másolása

    # Image összeállítása
    image = bytearray(total_sectors * sector_size)
    offset = 0
    # Boot szektor
    image[offset:offset + sector_size] = boot_sector
    offset += sector_size
    # FAT táblák
    for _ in range(fat_copies):
        image[offset:offset + sectors_per_fat * sector_size] = fat
        offset += sectors_per_fat * sector_size
    # Gyökérkönyvtár
    image[offset:offset + root_dir_entries * 32] = root_dir
    offset += root_dir_sectors * sector_size
    # Adat terület
    image[offset:offset + len(data_area)] = data_area

    # Fájlba írás
    with open('index.img', 'wb') as f:
        f.write(image)

if __name__ == '__main__':
    try:
        create_fat12_image()
    except FileNotFoundError as e:
        print(e)