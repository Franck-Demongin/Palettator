![palettator_hero_v0 1 0](https://github.com/user-attachments/assets/4f0adf69-0b06-4ef3-a121-fa355db1df4f)

<img src="https://img.shields.io/badge/Python-3.12-blue" /> [![GPLv3 license](https://img.shields.io/badge/License-GPLv3-green.svg)](http://perso.crans.org/besson/LICENSE.html)

# Palettator

Palettator is a tool that allows you to extract the color palette from an image.

## Installation

If GIT is installed, open a terminal where you want install Palettator and type:

```bash
git clone https://github.com/Franck-Demongin/Palettator.git
```

If GIT is not installed, retrieve the [ZIP](https://github.com/Franck-Demongin/Palettator/archive/refs/heads/main.zip) file, unzip it into where you want install Palettator. Rename it Palettator.

Open a terminal in the folder Palettator.  
Create a virtual env to isolate dependencies:

```bash
python -m venv .venv
```

_python_ should be replace by the right command according to your installation. On Linux, it could be _python3.10_ (or 3.11), on Windows _python.exe_

Activate the virtual environmant:

```bash
# Windows
.venv\Scripts\activate

# Linux
source .venv/bin/activae
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Generate palettes

- Full path to the image.
- 1 or /select: select one file.
- 2 or /multi: select multiple files.

*Examples:*
                    
/home/user_name/Desktop/image.png  
1 or 2 opens a file selector to choose the images to analyze.

Once one or more palettes have been generated, you can view the details of each palette, display the palette image and the source image, and export the palettes in different formats.

## View palette details

/s or /show [1-N] [-d or --display]  : display the RGB and hexadecimal values of the colors in a palette with:

- 1-N: palette index in the list.    
Leave blank to display the first palette in the list.  
- -d or --display: display the image.  
                  
*Examples:*
                                      
/s 1 -d    
/show 5    
/s -d

## Export the palette

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

## Display the list of palettes

Enter /l or /list: display the list of palettes.

## Configuration

Enter /c or /config: display the configuration.  
To change the default configuration, create (copy and rename the config.ini.example file to config.ini) or modify the config.ini file.

# Exit

Ctrl C or /exit 

## Changelog

### 0.1.0 - 2025-06-02

**Changed:**

- First version of Palettator
