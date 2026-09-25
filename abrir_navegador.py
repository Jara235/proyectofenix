"""
abrir_navegador.py - Gestor inteligente de pestañas para Sistema Fénix 2.0
Verifica si las páginas ya se encuentran abiertas en el navegador antes de abrirlas,
evitando la duplicación de pestañas.
"""
import sys
import os
import time
import subprocess
import webbrowser
import urllib.request
import ctypes
from ctypes import wintypes

MODULOS = [
    {
        'nombre': 'Dashboard Ejecutivo (Puerto 5000)',
        'puerto': 5000,
        'url': 'http://127.0.0.1:5000',
        'patrones': ['127.0.0.1:5000', 'localhost:5000', 'panel principal', 'dashboard ejecutivo', 'dashboard fénix', 'dashboard fenix']
    },
    {
        'nombre': 'Portal Captura en Campo (Puerto 5001)',
        'puerto': 5001,
        'url': 'http://127.0.0.1:5001',
        'patrones': ['127.0.0.1:5001', 'localhost:5001', 'portal captura', 'captura de datos', 'captura | fénix', 'captura | fenix']
    },
    {
        'nombre': 'Centro de Mando Administrativo (Puerto 5002)',
        'puerto': 5002,
        'url': 'http://127.0.0.1:5002',
        'patrones': ['127.0.0.1:5002', 'localhost:5002', 'centro de mando', 'iniciar sesión - centro de mando', 'iniciar sesion - centro de mando', 'reporte de conciliación']
    }
]

def obtener_titulos_ventanas_y_pestanas():
    titulos = set()
    
    # 1. Obtener títulos de ventanas usando la API nativa de Windows
    try:
        user32 = ctypes.windll.user32
        def enum_windows_proc(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    if buff.value:
                        titulos.add(buff.value.lower())
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        proc = WNDENUMPROC(enum_windows_proc)
        user32.EnumWindows(proc, 0)
    except Exception:
        pass

    # 2. Obtener nombres de pestañas en navegadores (Chrome, Edge, Brave, etc.) mediante UI Automation
    ps_cmd = """
    try {
        [System.Reflection.Assembly]::LoadWithPartialName("UIAutomationClient") | Out-Null
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $tabCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::TabItem)
        $tabs = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $tabCond)
        foreach ($t in $tabs) {
            if ($t.Current.Name) { Write-Output $t.Current.Name }
        }
    } catch {}
    """
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            l = line.strip().lower()
            if l:
                titulos.add(l)
    except Exception:
        pass

    return titulos

def esperar_servidor(puerto, max_intentos=8):
    url = f"http://127.0.0.1:{puerto}"
    for _ in range(max_intentos):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'FenixLauncher/1.0'})
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status in (200, 302):
                    return True
        except Exception:
            time.sleep(0.4)
    return False

def abrir_modulos(puerto_filtro=None):
    print("\n" + "=" * 60)
    print("  VERIFICANDO PESTAÑAS ABIERTAS DEL SISTEMA FÉNIX 2.0")
    print("=" * 60)
    
    titulos_abiertos = obtener_titulos_ventanas_y_pestanas()
    
    modulos_a_revisar = MODULOS
    if puerto_filtro:
        modulos_a_revisar = [m for m in MODULOS if m['puerto'] == puerto_filtro]
    
    for mod in modulos_a_revisar:
        nombre = mod['nombre']
        url = mod['url']
        patrones = mod['patrones']
        
        # Verificar si alguna ventana o pestaña coincide con los patrones del módulo
        ya_abierto = False
        for t in titulos_abiertos:
            if any(p in t for p in patrones):
                ya_abierto = True
                break
        
        if ya_abierto:
            print(f"  [✓ DETECTADO] {nombre}: YA está abierto en el navegador.")
        else:
            print(f"  [→ ABRIENDO]  {nombre} -> {url}...")
            # Esperar a que el servidor responda antes de abrir la pestaña
            esperar_servidor(mod['puerto'])
            # Abrir en el navegador predeterminado
            webbrowser.open(url)
            time.sleep(0.3)
            
    print("=" * 60 + "\n")

if __name__ == '__main__':
    filtro = None
    if len(sys.argv) > 1:
        try:
            filtro = int(sys.argv[1])
        except ValueError:
            pass
    abrir_modulos(filtro)
