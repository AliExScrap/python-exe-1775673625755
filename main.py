import webview
import subprocess
import socket
import time
import threading
import os
import sys

# Detection de l'utilisation du port n8n
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def launch_n8n():
    if is_port_in_use(5678):
        return True
    
    # Tentative 1: n8n start (si dans le PATH)
    try:
        subprocess.Popen(['n8n', 'start'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except FileNotFoundError:
        pass
    
    # Tentative 2: npx n8n start
    try:
        # shell=True est necessaire pour npx sur certains systemes Windows
        subprocess.Popen('npx n8n start', 
                         shell=True,
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception:
        return False

def monitor_and_load(window):
    success = launch_n8n()
    
    if not success:
        error_html = \"\"\"
        <div style='color:white;text-align:center;padding:50px;font-family:sans-serif;background:#1a1a1a;height:100vh;'>
            <h2 style='color:#ff6d5a;'>Erreur Critique</h2>
            <p>n8n n'est pas installe sur ce systeme.</p>
            <p style='font-size:0.9em;color:#aaa;'>Veuillez installer Node.js puis lancer :<br><code>npm install n8n -g</code></p>
        </div>
        \"\"\"
        window.load_html(error_html)
        return

    # Attente active du demarrage du service (max 45 secondes)
    retries = 45
    while retries > 0:
        if is_port_in_use(5678):
            # Petit delai supplementaire pour laisser l'API se stabiliser
            time.sleep(1)
            window.load_url('http://localhost:5678')
            return
        time.sleep(1)
        retries -= 1
    
    timeout_html = \"\"\"
    <div style='color:white;text-align:center;padding:50px;font-family:sans-serif;background:#1a1a1a;height:100vh;'>
        <h2 style='color:#ff6d5a;'>Delai depasse</h2>
        <p>n8n met trop de temps a demarrer ou le port 5678 est bloque.</p>
    </div>
    \"\"\"
    window.load_html(timeout_html)

if __name__ == '__main__':
    # Page de chargement avec CSS
    loader_html = \"\"\"
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { background: #121212; color: white; font-family: 'Segoe UI', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden; }
            .loader-container { width: 300px; text-align: center; }
            .progress-bg { width: 100%; height: 6px; background: #333; border-radius: 3px; overflow: hidden; margin-top: 20px; }
            .progress-bar { width: 40%; height: 100%; background: #ff6d5a; border-radius: 3px; animation: loading 2s infinite ease-in-out; }
            @keyframes loading { 
                0% { transform: translateX(-100%); } 
                100% { transform: translateX(250%); } 
            }
            h3 { font-weight: 300; letter-spacing: 1px; }
        </style>
    </head>
    <body>
        <div class="loader-container">
            <h3>INITIALISATION N8N</h3>
            <div class="progress-bg">
                <div class="progress-bar"></div>
            </div>
            <p style="font-size: 12px; color: #777; margin-top: 10px;">Verification du service...</p>
        </div>
    </body>
    </html>
    \"\"\"
    
    window = webview.create_window('n8n Desktop Launcher', html=loader_html, width=1280, height=800, background_color='#121212')
    
    # Lancement du check dans un thread separe
    threading.Thread(target=monitor_and_load, args=(window,), daemon=True).start()
    
    webview.start()
