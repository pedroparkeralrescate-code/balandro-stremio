# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json

MANIFEST = {
    "id": "community.balandro",
    "version": "1.0.0",
    "name": "Balandro [ES]",
    "description": "Películas y Series en Español - 127 Proveedores + 92 Servers",
    "logo": "https://i.imgur.com/placeholder.png",
    "background": "https://i.imgur.com/placeholder-bg.png",
    "resources": [
        "catalog",
        "stream"
    ],
    "types": ["movie", "series"],
    "catalogs": [
        {
            "type": "movie",
            "id": "balandro-movies",
            "name": "Balandro Películas",
            "extra": [
                {
                    "name": "genre",
                    "isRequired": False,
                    "options": ["Acción", "Aventura", "Animación", "Comedia", "Crimen", 
                               "Drama", "Fantasía", "Terror", "Romance", "Ciencia Ficción", 
                               "Thriller", "Western", "Guerra", "Documental"]
                },
                {
                    "name": "skip",
                    "isRequired": False
                }
            ]
        },
        {
            "type": "series",
            "id": "balandro-series",
            "name": "Balandro Series",
            "extra": [
                {
                    "name": "genre",
                    "isRequired": False,
                    "options": ["Acción", "Aventura", "Animación", "Comedia", "Crimen", 
                               "Drama", "Fantasía", "Terror", "Romance", "Ciencia Ficción", 
                               "Thriller", "Western", "Guerra", "Documental"]
                },
                {
                    "name": "skip",
                    "isRequired": False
                }
            ]
        }
    ],
    "idPrefixes": ["tt", "balandro"],
    "behaviorHints": {
        "configurable": False,
        "configurationRequired": False
    }
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(MANIFEST, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
