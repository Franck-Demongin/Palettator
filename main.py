# -*- coding: UTF-8 -*-

import os
from math import ceil
from PIL import Image, ImageDraw, ImageFont
import configparser
from Pylette import extract_colors, Palette
from rich.console import Console, JustifyMethod
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
from rich.markdown import Markdown
from dataclasses import dataclass

from modules.image_selector import select_images
from modules.export import Exporter, ExportToJSon, ExportToCSV, ExportToGPL, ExportToACO

console = Console()

# Configuration
VERSION = "0.1.0"
TITLE = "Palette From Image"
LOGO = "[bold]PALETTATOR[/bold]"

BASEDIR = os.path.dirname(os.path.abspath(__file__))

config_user = configparser.ConfigParser()
config_user.read(f"{BASEDIR}/config.ini")

config = {
    "palette": {
        "palette_size": config_user.getint('palette', 'palette_size', fallback=9),
        "square_x": config_user.getint('palette', 'square_x', fallback=100),
        "square_y": config_user.getint('palette', 'square_y', fallback=100),
        "columns": config_user.getint('palette', 'columns', fallback=3),
        "title_size": config_user.getint('palette', 'title_size', fallback=18),
        "subtitle_size": config_user.getint('palette', 'subtitle_size', fallback=14),
        "title_font": config_user.get('palette', 'title_font', fallback="Lato-Black.ttf"),
        "subtitle_font": config_user.get('palette', 'subtitle_font', fallback="Lato-Regular.ttf"),
        "resize": config_user.getboolean('palette', 'resize', fallback=True),
        "clear_console": config_user.getboolean('palette', 'clear_console', fallback=True),
        "save_path": config_user.get('palette', 'save_path', fallback=os.path.join(BASEDIR, "output")),
    }
}

@dataclass
class PaletteObject():
    palette: Palette
    image_path: str
    palette_path: str

@dataclass
class PaletteList():
    palettes: list[PaletteObject]

def print_hero(content: str, title: str="", version: str="", justify: JustifyMethod="center", model: str | None=None) -> None:
    console.line(1)
    console.print(
        Panel.fit(
            content,
            padding=(0, 20), 
            title=title if title else "",
            title_align="left",
            subtitle=f"{model + ' ─ ' if model else ''}{version if version else ''}",
            subtitle_align="right",
            style="green",
            border_style="white",
        ),
        justify=justify
    )
    console.line(1)

def get_image_info(image_path: str) -> tuple[str, str]:
    dirname = os.path.dirname(image_path)
    image_name = os.path.basename(image_path)

    return dirname, image_name

def get_palette(image_path: str) -> tuple[Palette, list]:
    palette = extract_colors(
        image=image_path, 
        palette_size=config["palette"]["palette_size"], 
        sort_mode='luminance', 
        resize=config["palette"]["resize"]
    )
    palette_rgb = palette_to_rgb(palette=palette)
    return palette, palette_rgb 

def palette_to_rgb(palette: Palette) -> list:
    return [tuple(color.rgb) for color in palette]

def convert_rgb_to_hex(rgb: tuple) -> str:
    return ('#%02x%02x%02x' % rgb).upper()

def create_palette_image(palette: Palette, palette_rgb: list, image_path: str) -> Image.Image:
    # Configuration
    square_x = config["palette"]['square_x']
    square_y = config["palette"]['square_y']
    columns = config["palette"]['columns']
    lines = ceil(len(palette.colors) / columns)
    title_size = config["palette"]['title_size']
    subtitle_size = config["palette"]['subtitle_size']
    title_font = config["palette"]['title_font']
    subtitle_font = config["palette"]['subtitle_font']
    
    # image size
    image_width = columns * square_x
    image_height = lines * square_y
    
    image = Image.new('RGB', (image_width, image_height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Chargement des polices
    try:
        font = ImageFont.truetype(f"{BASEDIR}/fonts/{title_font}", title_size)
        font_subtitle = ImageFont.truetype(f"{BASEDIR}/fonts/{subtitle_font}", subtitle_size)
    except:
        font = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
    
    # Génération des carrés de couleur
    for i, (color, rgb) in enumerate(zip(palette.colors, palette_rgb)):
        # Calcul de la position
        col = i % columns
        ligne = i // columns
        
        x = col * square_x
        y = ligne * square_y
        
        color_hex = convert_rgb_to_hex(rgb)

        # Dessin du carré de couleur
        draw.rectangle(
            [x, y, x + square_x, y + square_y],
            fill=rgb,
            outline=color_hex,
            width=5
        )
        
        # Taille du texte
        title_length = font.getlength(color_hex)
        # position du texte
        text_x = x + square_x // 2 - title_length // 2
        if square_x < square_y:
            text_y = y + square_x // 2 - title_size // 2
        else:
            text_y = y + square_y // 2 - title_size // 2

        subtitle_text = f"{color.freq*100:.2f}%"
        subtitle_length = font_subtitle.getlength(subtitle_text)
        subtitle_x = x + square_x // 2 - subtitle_length // 2
        subtitle_y = text_y + title_size + subtitle_size // 2

        color_text = (0, 0, 0) if color.luminance > 200 else (255, 255, 255)
        draw.text((text_x, text_y), color_hex, fill=color_text, font=font)
        draw.text((subtitle_x, subtitle_y), subtitle_text, fill=color_text, font=font_subtitle)

    # image.show()
    return image

def save_palette(palette: Palette, palette_rgb: list, image_path: str) -> str:
    """Génère et sauvegarde l'image de la palette"""
    _, image_name = get_image_info(image_path)
    image_name = image_name.split('.')[0]
    image = create_palette_image(palette=palette, palette_rgb=palette_rgb, image_path=image_path)
    save_path = config["palette"]['save_path']
    if not os.path.exists(save_path) or not os.path.isdir(save_path):
        os.makedirs(save_path)
    file_path = os.path.join(save_path, f"{image_name}_palette.png")
    image.save(file_path)

    return file_path

def palette_info(palette_object: PaletteObject, indice: int, display: bool | None=False) -> None:
    """Affiche les informations sur la palette"""
    palette = palette_object.palette
    palette_rgb = palette_to_rgb(palette=palette)
    image_path = palette_object.image_path
    palette_path = palette_object.palette_path

    dirname, image_name = get_image_info(image_path)
    console.rule(f"PALETTE {indice}", style="bold blue")
    print()
    print(f"Directory : {dirname}")
    print(f"Name : {image_name}")
    print(f"Palette path : {palette_path}")
    print()

    for i, (color, rgb) in enumerate(zip(palette.colors, palette_rgb), 1):
        print(f"{i:2d}.  {rgb} - {('#%02x%02x%02x' % rgb).upper()} - {color.freq*100:.2f}%")

    print()
    console.rule("", style="bold blue")
    print()

    # show image
    if display:
        image_palette = Image.open(palette_path)
        image = Image.open(image_path)
        image.show()
        image_palette.show()

def get_indice_from_option(image_path: str, palettes_list: PaletteList, all: bool=False) -> int | None:
    indice_split = image_path.strip().split(' ')
    if len(indice_split) > 1:
        if indice_split[1].startswith(("-", "--")):
            indice = 1
        else:
            if all:
                if indice_split[1] in ["all", "ALL"]:
                    return -1
            try:
                indice = int(indice_split[1])
            except ValueError:
                return None
    else:
        indice = 1
    if indice is None or indice < 1 or indice > len(palettes_list.palettes):
        return None
    return indice

def get_display_from_option(image_path: str) -> bool:
    option_split = image_path.strip().split(' ')
    if len(option_split) > 1 and option_split[1] in ["-d", "--display"]:
        return True
    if len(option_split) > 2 and option_split[2] in ["-d", "--display"]:
        return True
    return False

def get_action_from_option(image_path: str) -> str:
    option_split = image_path.strip().split(' ')
    return option_split[0][1:]

def export_csv(palettes_list: PaletteList, indice: int = 0) -> None:
    console.rule("Exporting to CSV", style="bold blue")
    exporter = ExportToCSV()
    export(exporter=exporter, palettes_list=palettes_list, indice=indice, extension="csv")

def export_json(palettes_list: PaletteList, indice: int = 0) -> None:
    console.rule("Exporting to JSON", style="bold blue")
    exporter = ExportToJSon()
    export(exporter=exporter, palettes_list=palettes_list, indice=indice, extension="json")

def export_gpl(palettes_list: PaletteList, indice: int = 0) -> None:
    console.rule("Exporting to GPL", style="bold blue")
    exporter = ExportToGPL()
    export(exporter=exporter, palettes_list=palettes_list, indice=indice, extension="gpl")

def export_aco(palettes_list: PaletteList, indice: int = 0) -> None:
    console.rule("Exporting to ACO", style="bold blue")
    exporter = ExportToACO()    
    export(exporter=exporter, palettes_list=palettes_list, indice=indice, extension="aco")

def export(exporter: Exporter, palettes_list: PaletteList, indice: int, extension: str) -> None:
    if indice == -1:
        palettes = palettes_list.palettes
    else:
        palettes = [palettes_list.palettes[indice-1]]
    
    save_path = config["palette"]['save_path']
    if not os.path.exists(save_path) or not os.path.isdir(save_path):
        os.makedirs(save_path)

    console.line()   
    for index, palette in enumerate(palettes):
        _, image_name = get_image_info(palette.image_path)
        image_name = image_name.split('.')[0]
        file_name = f"{image_name}_palette.{extension}"
        file_path = os.path.join(save_path, file_name)
        palette_rgb = palette_to_rgb(palette=palette.palette)
        palette_hex = [convert_rgb_to_hex(tuple(color.rgb)) for color in palette.palette]
        exporter.export(palette_name=image_name, filepath=file_path, palette_rgb=palette_rgb, palette_hex=palette_hex)
        console.print(f"{index+1:2d} >  Palette exported to {file_name}", style="green")

    print_end()

def list_palettes(palettes_list: PaletteList) -> None:
    console.rule(f"PALETTE{'S' if len(palettes_list.palettes) > 1 else ''}", style="bold blue")
    console.line()
    for i, palette_object in enumerate(palettes_list.palettes):
        _, image_name = get_image_info(palette_object.image_path)
        console.print(f"{i+1:2d} >  [bold]{image_name}[/bold]", style="green")

    print_end()

def print_header():
    console.line()
    print_hero(
        content=LOGO,
        title=TITLE,
        version=VERSION
    )
    console.line()

def print_config():
    console.rule("Configuration", style="bold blue")
    console.line()
    console.print(config)
    print_end()


def print_help(show_palette_max: int=0):
    if show_palette_max == 0:
        console.print("> [green bold]Full path to the image[/]", highlight=False)
        console.print("> [green bold]1 or /select[/] [italic]select one file[/]", highlight=False)
        console.print("> [green bold]2 or /multi[/] [italic]select multiple files[/]", highlight=False)
        console.print("> [green bold]/c or /config[/] [italic]display configuration[/]", highlight=False)
        console.print("> [green bold]/h or /help[/] [italic]display help[/]", highlight=False)
        console.print("> [green bold]Ctrl C ou /exit[/] [italic]exit[/]", highlight=False)
    else:
        console.print("> [green bold]1 or 2 [/] [italic]selection[/] -  [green bold]Ctrl C ou /exit[/] [italic]exit[/] - [green bold]/h or /help[/] [italic]display help[/]", highlight=False)
        console.print(f"> [green bold]/s or /show [1-{show_palette_max}] [-d ou --display][/] [italic]view palette details[/]", highlight=False)
        console.print(f"> [green bold]/(csv | json | gpl | aco) ALL | [1-{show_palette_max}][/] [italic]export palette[/]", highlight=False)
        console.print("> [green bold]/l or /list[/] [italic]display palette list[/]", highlight=False)
    console.line()

def print_instructions():
    console.rule("Utilisation", style="bold blue")
    console.line()
    md = Markdown("""Palettator is a tool that allows you to extract the color palette from an image.
                  

**Generate palettes**

- Full path to the image.
- 1 or /select: select one file.
- 2 or /multi: select multiple files.

*Examples:*
                    
/home/user_name/Desktop/image.png  
1 or 2 opens a file selector to choose the images to analyze.

Once one or more palettes have been generated, you can view the details of each palette, display the palette image and the source image, and export the palettes in different formats.

**View palette details**

/s or /show [1-N] [-d or --display]  : display the RGB and hexadecimal values of the colors in a palette with:

- 1-N: palette index in the list.    
Leave blank to display the first palette in the list.  
- -d or --display: display the image.  
                  
*Examples:*
                                      
/s 1 -d    
/show 5    
/s -d

**Export the palette**

Palettes can be exported in CSV, JSON, GPL (Gimp), and ACO (Adobe) formats.  
Enter /(csv | json | gpl | aco) ALL | [1-N], with:

- ALL: all palettes in the list.  
- 1-N: palette index.  
- empty to select the first (or only) palette in the list.
                  
*Examples:*   
                                  
/csv 1    
/aco ALL
/json

The corresponding files are saved in the same directory as the palette images.

**Display the list of palettes**

Enter /l or /list: display the list of palettes.

**Configuration**

Enter /c or /config: display the configuration.  
To change the default configuration, create (copy and rename the config.ini.example file to config.ini) or modify the config.ini file.

**Exit**

Ctrl C or /exit 
""")
    console.print(md)
    
    print_end()

def print_end():
    console.line()
    console.rule("", style="bold blue")
    console.line()
    

def main():
    palettes_list = PaletteList(palettes=[])

    print_header()
    action = 'generate'
    try: 
        while True: 

            if action != 'help': 
                print_help(show_palette_max=len(palettes_list.palettes))

            while True:
                action = 'generate'
                indice = 0
                display = None
                image_path = input("Option : ")
                if image_path == "/exit":
                    print()
                    exit()
                elif image_path in ["/h", "/help"]:
                    action = 'help'
                    break
                elif image_path in ["/c", "/config"]:
                    action = 'config'
                    break
                elif image_path.startswith(("/s", "/show")):
                    action = 'show'
                    if indice:= get_indice_from_option(image_path, palettes_list):
                        display = get_display_from_option(image_path)
                        break
                    console.print("Invalid palette index.", style="red")
                    continue
                elif image_path.startswith(("/csv", "/json", "/gpl", "/aco")):
                    action = get_action_from_option(image_path)
                    if indice:= get_indice_from_option(image_path, palettes_list, all=True):
                        break
                    console.print("Invalid palette index.", style="red")
                    continue
                elif image_path.startswith(("/l", "/list")):
                    if len(palettes_list.palettes) == 0:
                        console.print("No palette available.", style="red")
                        continue    
                    action = 'list'
                    break
                elif os.path.exists(image_path):
                    if os.path.isfile(image_path):
                        break
                    else:
                        console.print("Only files are allowed.", style="red")
                elif image_path == "1" or image_path == "/select":
                    image_path = select_images(multiple=False, title="Choose an image")
                    if image_path is not None:
                        break
                    else:
                        console.print("No file has been selected.", style="red")
                elif image_path == "2" or image_path == "/multi":
                    image_path = select_images(multiple=True, title="Choose one or more images")
                    if image_path is not None:
                        break
                    else:
                        console.print("No file has been selected.", style="red")
                else:
                    console.print("Please enter a valid path.", style="red")
            
            if config["palette"]["clear_console"]:
                console.clear()
                print_header()
                console.line()
            
            if action == 'help':
                print_instructions()
                continue
            if action == 'config':
                print_config()
                continue
            if action == 'show':
                palette_info(palette_object=palettes_list.palettes[indice - 1], indice=indice, display=display)
                continue           
            if action == 'csv':
                export_csv(palettes_list=palettes_list, indice=indice)
                continue
            if action == 'json':
                export_json(palettes_list=palettes_list, indice=indice)
                continue
            if action == 'gpl':
                export_gpl(palettes_list=palettes_list, indice=indice)
                continue
            if action == 'aco':
                export_aco(palettes_list=palettes_list, indice=indice)
                continue
            if action == 'list':
                list_palettes(palettes_list=palettes_list)
                continue
            
            # Extraction des palettes
            palettes_list.palettes = []
            if isinstance(image_path, str):
                images = [image_path]
            else:
                images = image_path
            
            with Progress(
                    SpinnerColumn(), 
                    TextColumn("[progress.description]{task.description}"), 
                    BarColumn(), 
                    MofNCompleteColumn(), 
                    transient=True
                ) as progress:
                progress_title = f"Extracting palette{'s' if len(images) > 1 else ''}"
                task = progress.add_task(progress_title, total=len(images))
                for image_path in images:
                    palette, palette_rgb = get_palette(image_path)
                
                    # Génération et sauvegarde de l'image
                    try:
                        _, image_name = get_image_info(image_path)
                        palette_path = save_palette(palette=palette, palette_rgb=palette_rgb, image_path=image_path)
                        palettes_list.palettes.append(PaletteObject(palette=palette, image_path=image_path, palette_path=palette_path))
                        
                    except Exception as e:
                        print(f"❌ Error during generation: {e}")
                        print("Check the installation of dependencies")
                    
                    progress.update(task, advance=1)
            
            list_palettes(palettes_list=palettes_list)

    except KeyboardInterrupt:
        print()
        exit()   

if __name__ == "__main__":
    main()
    
