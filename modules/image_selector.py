"""
Sélecteur d'images portable avec interface graphique native
Compatible Windows, macOS, Linux avec fallback
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union

class DialogResult:
    """Classe pour distinguer les différents résultats du dialogue"""
    def __init__(self, success: bool, cancelled: bool, data: Optional[Union[str, List[str]]]):
        self.success = success      # True si la méthode a fonctionné techniquement
        self.cancelled = cancelled  # True si l'utilisateur a annulé
        self.data = data           # Les données sélectionnées

def select_images_tkinter(multiple: bool = True, title: str = "Sélectionner des images") -> DialogResult:
    """
    Sélectionneur d'images utilisant tkinter (inclus dans Python)
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Créer une fenêtre root cachée
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale
        root.lift()      # Mettre au premier plan
        root.attributes('-topmost', True)  # Toujours au-dessus
        
        # Types de fichiers d'images supportés
        filetypes = [
            ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("GIF", "*.gif")
        ]
        
        try:
            if multiple:
                files = filedialog.askopenfilenames(
                    title=title,
                    filetypes=filetypes
                )
                if files:
                    return DialogResult(True, False, list(files))
                else:
                    return DialogResult(True, True, None)  # Annulé par l'utilisateur
            else:
                file = filedialog.askopenfilename(
                    title=title,
                    filetypes=filetypes
                )
                if file:
                    return DialogResult(True, False, file)
                else:
                    return DialogResult(True, True, None)  # Annulé par l'utilisateur
        finally:
            root.destroy()
            
    except ImportError:
        return DialogResult(False, False, None)  # Échec technique

def select_images_qt(multiple: bool = True, title: str = "Sélectionner des images") -> DialogResult:
    """
    Sélectionneur d'images utilisant PyQt5/PySide2 (fallback)
    """
    try:
        # Essayer PyQt5 en premier
        try:
            from PyQt5.QtWidgets import QApplication, QFileDialog # type: ignore
            from PyQt5.QtCore import Qt # type: ignore
        except ImportError:
            # Fallback vers PySide2
            from PySide2.QtWidgets import QApplication, QFileDialog # type: ignore
            from PySide2.QtCore import Qt # type: ignore
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Types de fichiers
        filter_str = "Images (*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp)"
        
        if multiple:
            files, _ = QFileDialog.getOpenFileNames(
                None,
                title,
                "",
                filter_str
            )
            if files:
                return DialogResult(True, False, files)
            else:
                return DialogResult(True, True, None)  # Annulé
        else:
            file, _ = QFileDialog.getOpenFileName(
                None,
                title,
                "",
                filter_str
            )
            if file:
                return DialogResult(True, False, file)
            else:
                return DialogResult(True, True, None)  # Annulé
            
    except ImportError:
        return DialogResult(False, False, None)  # Échec technique

def select_images_zenity(multiple: bool = True, title: str = "Sélectionner des images") -> DialogResult:
    """
    Sélectionneur d'images utilisant zenity (Linux uniquement)
    """
    if os.name != 'posix':
        return DialogResult(False, False, None)  # Pas Linux
        
    try:
        import subprocess
        
        cmd = [
            'zenity', '--file-selection',
            f'--title={title}',
            '--file-filter=Images | *.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp'
        ]
        
        if multiple:
            cmd.append('--multiple')
            cmd.append('--separator=|')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if multiple:
                files = output.split('|') if output else []
                return DialogResult(True, False, files if files else None)
            else:
                return DialogResult(True, False, output if output else None)
        elif result.returncode == 1:
            # Code 1 = annulé par l'utilisateur
            return DialogResult(True, True, None)
        else:
            # Autre code d'erreur = problème technique
            return DialogResult(False, False, None)
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError): # type: ignore
        return DialogResult(False, False, None)  # Échec technique

def select_images_windows_native(multiple: bool = True, title: str = "Sélectionner des images") -> DialogResult:
    """
    Sélectionneur d'images utilisant les API Windows natives (Windows 10/11)
    Utilise IFileOpenDialog pour un look moderne
    """
    if os.name != 'nt':
        return DialogResult(False, False, None)  # Pas Windows
        
    try:
        # Essayer d'abord avec win32gui (plus simple et fiable)
        try:
            import win32gui
            import win32con
            import pywintypes
            
            filter_str = "Images\0*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.webp\0"
            
            try:
                if multiple:
                    filename, customfilter, flags = win32gui.GetOpenFileNameW(
                        InitialDir=os.getcwd(),
                        Flags=win32con.OFN_ALLOWMULTISELECT | win32con.OFN_EXPLORER | win32con.OFN_FILEMUSTEXIST,
                        File='',
                        DefExt='jpg',
                        Title=title,
                        Filter=filter_str,
                        FilterIndex=1
                    )
                    
                    if filename:
                        # Parser les fichiers multiples
                        files = filename.split('\0')
                        if len(files) > 1:
                            directory = files[0]
                            result = [os.path.join(directory, f) for f in files[1:] if f]
                            return DialogResult(True, False, result)
                        else:
                            return DialogResult(True, False, [filename])
                    else:
                        return DialogResult(True, True, None)  # Annulé
                else:
                    filename, customfilter, flags = win32gui.GetOpenFileNameW(
                        InitialDir=os.getcwd(),
                        Flags=win32con.OFN_FILEMUSTEXIST,
                        File='',
                        DefExt='jpg',
                        Title=title,
                        Filter=filter_str,
                        FilterIndex=1
                    )
                    if filename:
                        return DialogResult(True, False, filename)
                    else:
                        return DialogResult(True, True, None)  # Annulé
                        
            except pywintypes.error as e:
                # L'utilisateur a annulé ou erreur dialogue
                if e.winerror == 0:  # ERROR_SUCCESS mais pas de fichier = annulé
                    return DialogResult(True, True, None)
                else:
                    return DialogResult(False, False, None)  # Erreur technique
                    
        except ImportError:
            # win32gui non disponible, essayer COM direct
            import ctypes
            from ctypes import wintypes, byref
            
            # Implementation COM basique (simplifié)
            ole32 = ctypes.windll.ole32
            ole32.CoInitialize(None)
            
            try:
                # Pour simplifier, on utilise GetOpenFileName de comdlg32
                comdlg32 = ctypes.windll.comdlg32
                
                class OPENFILENAME(ctypes.Structure):
                    _fields_ = [
                        ('lStructSize', wintypes.DWORD),
                        ('hwndOwner', wintypes.HWND),
                        ('hInstance', wintypes.HINSTANCE),
                        ('lpstrFilter', wintypes.LPCWSTR),
                        ('lpstrCustomFilter', wintypes.LPWSTR),
                        ('nMaxCustFilter', wintypes.DWORD),
                        ('nFilterIndex', wintypes.DWORD),
                        ('lpstrFile', wintypes.LPWSTR),
                        ('nMaxFile', wintypes.DWORD),
                        ('lpstrFileTitle', wintypes.LPWSTR),
                        ('nMaxFileTitle', wintypes.DWORD),
                        ('lpstrInitialDir', wintypes.LPCWSTR),
                        ('lpstrTitle', wintypes.LPCWSTR),
                        ('Flags', wintypes.DWORD),
                        ('nFileOffset', wintypes.WORD),
                        ('nFileExtension', wintypes.WORD),
                        ('lpstrDefExt', wintypes.LPCWSTR),
                        ('lCustData', wintypes.LPARAM),
                        ('lpfnHook', wintypes.LPVOID),
                        ('lpTemplateName', wintypes.LPCWSTR),
                    ]
                
                ofn = OPENFILENAME()
                ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
                
                buffer_size = 32768 if multiple else 260
                file_buffer = ctypes.create_unicode_buffer(buffer_size)
                
                ofn.lpstrFile = file_buffer
                ofn.nMaxFile = buffer_size
                ofn.lpstrFilter = "Images\0*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.webp\0"
                ofn.lpstrTitle = title
                ofn.Flags = 0x1000 | 0x4  # OFN_FILEMUSTEXIST | OFN_HIDEREADONLY
                
                if multiple:
                    ofn.Flags |= 0x200  # OFN_ALLOWMULTISELECT
                
                result = comdlg32.GetOpenFileNameW(byref(ofn))
                
                if result:
                    if multiple:
                        # Parser la sortie multi-sélection
                        files_str = file_buffer.value
                        files = files_str.split('\0')
                        files = [f for f in files if f]  # Enlever les chaînes vides
                        
                        if len(files) > 1:
                            directory = files[0]
                            result_files = [os.path.join(directory, f) for f in files[1:]]
                            return DialogResult(True, False, result_files)
                        elif len(files) == 1:
                            return DialogResult(True, False, [files[0]])
                        else:
                            return DialogResult(True, True, None)
                    else:
                        return DialogResult(True, False, file_buffer.value)
                else:
                    # Vérifier si c'est une annulation ou une erreur
                    error_code = ctypes.windll.comdlg32.CommDlgExtendedError()
                    if error_code == 0:
                        return DialogResult(True, True, None)  # Annulé par l'utilisateur
                    else:
                        return DialogResult(False, False, None)  # Erreur technique
                        
            finally:
                ole32.CoUninitialize()
                
    except Exception:
        return DialogResult(False, False, None)  # Échec technique

def select_images_applescript(multiple: bool = True, title: str = "Sélectionner des images") -> Optional[Union[str, List[str]]]:
    """
    Sélectionneur d'images utilisant AppleScript (macOS uniquement)
    """
    if sys.platform != 'darwin':
        return None
        
    try:
        import subprocess
        
        if multiple:
            script = f'''
            tell application "System Events"
                set imageFiles to choose file with prompt "{title}" ¬
                    of type {{"public.image"}} ¬
                    with multiple selections allowed
                set filePaths to {{}}
                repeat with imageFile in imageFiles
                    set end of filePaths to POSIX path of imageFile
                end repeat
                return my list_to_string(filePaths, "|")
            end tell
            
            on list_to_string(lst, delim)
                set AppleScript's text item delimiters to delim
                set txt to lst as string
                set AppleScript's text item delimiters to ""
                return txt
            end list_to_string
            '''
        else:
            script = f'''
            tell application "System Events"
                set imageFile to choose file with prompt "{title}" ¬
                    of type {{"public.image"}}
                return POSIX path of imageFile
            end tell
            '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if multiple:
                return output.split('|') if output else None
            else:
                return output if output else None
        return None
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return None

def select_images(multiple: bool = True, title: str = "Sélectionner des images") -> Optional[Union[str, List[str]]]:
    """
    Fonction principale pour sélectionner des images avec fallback automatique
    
    Args:
        multiple: Si True, permet la sélection multiple
        title: Titre de la fenêtre de dialogue
        
    Returns:
        str ou List[str] selon le mode, None si annulé ou échec
    """
    
    # Ordre de priorité des méthodes selon l'OS
    if sys.platform == 'darwin':  # macOS
        methods = [select_images_applescript, select_images_tkinter, select_images_qt]
    elif os.name == 'posix':      # Linux
        methods = [select_images_zenity, select_images_tkinter, select_images_qt]
    else:                         # Windows
        methods = [select_images_windows_native, select_images_tkinter, select_images_qt]
    
    # Essayer chaque méthode jusqu'à ce qu'une fonctionne techniquement
    for method in methods:
        try:
            result = method(multiple=multiple, title=title)
            
            if result.success:
                # La méthode a fonctionné techniquement
                if result.cancelled:
                    # L'utilisateur a annulé volontairement
                    return None
                else:
                    # L'utilisateur a sélectionné quelque chose
                    return result.data
            # Si result.success == False, essayer la méthode suivante
            
        except Exception as e:
            print(f"Erreur avec {method.__name__}: {e}", file=sys.stderr)
            continue
    
    # Si toutes les méthodes échouent techniquement
    print("Erreur: Impossible d'ouvrir le sélecteur de fichiers", file=sys.stderr)
    print("Assurez-vous d'avoir tkinter installé ou installez PyQt5/PySide2", file=sys.stderr)
    return None

def validate_images(file_paths: Union[str, List[str]]) -> List[Path]:
    """
    Valide que les fichiers sélectionnés sont des images
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    valid_files = []
    
    for file_path in file_paths:
        path = Path(file_path)
        if path.exists() and path.suffix.lower() in valid_extensions:
            valid_files.append(path)
        else:
            print(f"Attention: {file_path} n'est pas une image valide", file=sys.stderr)
    
    return valid_files

# Exemple d'utilisation
if __name__ == "__main__":
    print("=== Sélecteur d'images ===")
    
    # Sélection multiple
    print("\n1. Sélection multiple d'images:")
    images = select_images(multiple=True, title="Choisissez vos images")
    
    if images:
        print(f"Images sélectionnées: {len(images)}")
        valid_images = validate_images(images)
        for img in valid_images:
            print(f"  - {img}")
    else:
        print("Aucune image sélectionnée")
    
    # Sélection simple
    print("\n2. Sélection d'une seule image:")
    image = select_images(multiple=False, title="Choisissez une image")
    
    if image:
        print(f"Image sélectionnée: {image}")
        valid_images = validate_images(image)
        if valid_images:
            print(f"Image valide: {valid_images[0]}")
    else:
        print("Aucune image sélectionnée")