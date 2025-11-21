from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.manifest import MANIFEST
from api.streams import Streams
from api.catalog import Catalog
from api.meta import Meta

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Balandro Stremio Addon is running!"

@app.route('/manifest.json')
def manifest():
    return jsonify(MANIFEST)

@app.route('/catalog/<type>/<id>.json')
def catalog(type, id):
    # Parse skip from id if present (e.g. balandro-movies.json?skip=20 or inside id)
    # Stremio passes extra parameters in the ID sometimes or as query params?
    # Stremio format: /catalog/movie/top/skip=20.json
    
    # Check if id contains .json
    if id.endswith('.json'):
        id = id.replace('.json', '')
    
    skip = 0
    if 'skip=' in id:
        parts = id.split('skip=')
        id = parts[0]
        try:
            skip = int(parts[1])
        except:
            pass
    
    # Also check query params
    if request.args.get('skip'):
        try:
            skip = int(request.args.get('skip'))
        except:
            pass
            
    catalog_logic = Catalog()
    metas = catalog_logic.get_catalog(type, id, skip)
    return jsonify({"metas": metas})

@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    if id.endswith('.json'):
        id = id.replace('.json', '')
        
    season = request.args.get('season')
    episode = request.args.get('episode')
    
    streams_logic = Streams()
    streams = streams_logic.get_streams(type, id, season, episode)
    return jsonify({"streams": streams})

@app.route('/meta/<type>/<id>.json')
def meta(type, id):
    if id.endswith('.json'):
        id = id.replace('.json', '')
        
    meta_logic = Meta()
    meta_data = meta_logic.get_meta(type, id)
    return jsonify({"meta": meta_data})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
