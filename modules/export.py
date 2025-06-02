import csv
import os
import json
from abc import ABC, abstractmethod
from math import floor

class Exporter(ABC):
    """Formatting palette colors to export in a specific format."""
    
    @abstractmethod
    def export(self, palette_name: str, filepath: str, palette_rgb: list[tuple[int, int, int]], palette_hex: list[str]) -> None:
        """Export colors"""

class ExportToJSon(Exporter):

    def export(self, palette_name: str, filepath: str, palette_rgb: list[tuple[int, int, int]], palette_hex: list[str]) -> None:
        rgb = [(int(color[0]), int(color[1]), int(color[2])) for color in palette_rgb]
        output = {
            "name": palette_name,
            "rgb": rgb,
            "hex": palette_hex
        }  
        with open(filepath, 'w') as f:
            json.dump(output, f)

class ExportToCSV(Exporter):

    def export(self, palette_name: str, filepath: str, palette_rgb: list[tuple[int, int, int]], palette_hex: list[str]) -> None:
        _ = palette_name
        with open(filepath, 'w', newline='') as csv_file:
            header = ['R', 'G', 'B', 'HEX']
            writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for rgb, hex in zip(palette_rgb, palette_hex):
                writer.writerow({'R': rgb[0], 'G': rgb[1], 'B': rgb[2], 'HEX': hex})


class ExportToGPL(Exporter):

    def export(self, palette_name: str, filepath: str, palette_rgb: list[tuple[int, int, int]], palette_hex: list[str]) -> None:
        nl = "\n"
        output = (f"GIMP Palette\n"
            f"Name: {palette_name}\n"
            f"Columns: 5\n"
            f"#\n"
            f"# Number : {len(palette_rgb)}\n"
            f"#\n")
        for i, color in enumerate(palette_rgb):
            output += f"{color[0]} {color[1]} {color[2]} Index {i}\n"

        with open(filepath, 'w') as f:
            f.write(output)

class ExportToACO(Exporter):

    def export(self, palette_name: str, filepath: str, palette_rgb: list[tuple[int, int, int]], palette_hex: list[str]) -> None:
        nb = len(palette_rgb)
        nb_1 = floor(nb/255)
        nb_2 = nb%255

        with open(filepath, 'wb') as f:
            f.write(bytearray([0, 1]))
            f.write(bytearray([nb_1, nb_2]))
        
            for color in palette_rgb:
                f.write(bytearray([0,0,color[0],color[0],color[1],color[1],color[2],color[2],0,0]))
