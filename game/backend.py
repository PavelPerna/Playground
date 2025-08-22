api_key = ""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from xai_sdk import Client
from xai_sdk.chat import user, system
import logging
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

app = Flask(__name__)
CORS(app)  # Povolí CORS pro všechny požadavky

# Nastavení logování
logging.basicConfig(filename='backend_error.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# --- UPDATED DATA MODELS ---
@dataclass
class Character:
    """Represents a game character with detailed attributes."""
    name: str
    appearance: str = ""
    personality: str = ""
    sexuality: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict) # e.g., {"strength": 10, "intelligence": 8}
    skills: List[str] = field(default_factory=list) # e.g., ["sneaking", "persuasion"]

@dataclass
class Story:
    """Represents a custom story with extended context."""
    action: str
    response: str
    location: str
    characters: List[str] = field(default_factory=list) # Names of characters involved
    history_context: List[str] = field(default_factory=list) # Relevant past events for this story
    goal: str = "" # FIX: Added a default value to 'goal' to resolve TypeError
    # inventory is now part of the action's effect, not necessarily the story's core definition
    # The 'scene' from previous story model will implicitly be the 'response' leading to a new 'scene' in Grok output


@dataclass
class Location:
    """Represents a game location."""
    name: str
    desc: str = "" # Added default value for consistency with other models

# Example usage (not persistent, just for demonstrating the models)
# characters_data: List[Character] = []
# stories_data: Dict[str, Story] = {} # Keyed by action
# locations_data: List[Location] = {} # Changed to dict for easier lookup by name
# --- END UPDATED DATA MODELS ---

@app.route('/api/grok', methods=['OPTIONS'])
def grok_options():
    resp = jsonify({'status': 'ok'})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    logging.debug('Handled OPTIONS request for /api/grok')
    return resp, 200

@app.route('/api/grok', methods=['POST'])
def grok():
    try:
        data = request.get_json()
        if not data:
            error_msg = 'No JSON data received'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 400

        prompt = data.get('prompt')
        max_tokens = data.get('max_tokens')
        temperature = data.get('temperature')
        
        # Additional context data from frontend (these are passed to Grok as part of the prompt context)
        history = data.get('history', [])
        characters_list = data.get('characters', []) # This will now contain richer character data
        inventory = data.get('inventory', [])
        current_scene = data.get('current_scene', '')
        locations_list = data.get('locations', []) # This will now contain richer location data

        if not all([prompt, max_tokens, temperature]):
            error_msg = 'Missing required parameters: ' + ', '.join([k for k, v in {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}.items() if not v])
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 400

        logging.debug(f'Received POST request: prompt={prompt}, max_tokens={max_tokens}, temperature={temperature}')
        # Log the full context for debugging
        logging.debug(f'Context data: history={history}, characters={characters_list}, inventory={inventory}, scene={current_scene}, locations={locations_list}')


        # Inicializace xAI SDK klienta
        if not api_key:
            error_msg = 'XAI_API_KEY environment variable not set.'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 500

        try:
            client = Client(api_key=api_key)
            chat = client.chat.create(model="grok-3", max_tokens=max_tokens, temperature=temperature)
            
            # --- UPDATED SYSTEM PROMPT FOR JSON FORMAT ADHERENCE ---
            # This prompt now reinforces the expected structure and language rules more strongly.
            chat.append(system(
                "Jsi zvrhlý vypravěč špinavé hry. "
                "Odpovídej vždy striktně v JSON formátu. "
                "Klíče JSONu (např. 'output', 'scene', 'choices') musí být vždy v angličtině, "
                "ale jejich hodnoty (texty) v češtině. "
                "Zde je očekávaná struktura: "
                "{\"output\": \"<Vypravěčova odpověď na akci hráče, v češtině.>\", "
                "\"scene\": \"<Kompletní popis nové scény po akci, v češtině.>\", "
                "\"choices\": [\"<Možnost 1, v češtině>\", \"<Možnost 2, v češtině>\", \"<Možnost 3, v češtině>\"]}"
            ))
            # --- END UPDATED SYSTEM PROMPT ---
            
            # Constructing a more detailed user prompt for Grok including all relevant context
            full_prompt = f"""
            Hráč provedl akci: "{prompt}"

            Aktuální scéna: "{current_scene}"
            Inventář hráče: {', '.join(inventory) if inventory else 'žádný předmět'}
            Historie posledních akcí: {'; '.join(history[-5:]) if history else 'žádná historie'}

            Postavy ve hře:
            {json.dumps(characters_list, ensure_ascii=False, indent=2)}

            Lokace ve hře:
            {json.dumps(locations_list, ensure_ascii=False, indent=2)}

            Vytvoř novou scénu, vypravěčovu odpověď na akci hráče a 3 nové možnosti akcí.
            Odpověz striktně v daném JSON formátu.
            """
            chat.append(user(full_prompt))

            response = chat.sample()
            content = response.content

            if not content:
                logging.error('Empty content in response from xAI SDK')
                return jsonify({'error': 'Empty content from xAI SDK'}), 500

            logging.debug(f'Response from xAI SDK: {content}')
            resp = jsonify({
                'choices': [{'message': {'content': content, 'role': 'assistant'}}]
            })
            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return resp
        except Exception as e:
            error_msg = f'xAI SDK error: {str(e)}'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 500

    except json.JSONDecodeError as e:
        error_msg = f'Failed to decode JSON object: {str(e)}'
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 400

if __name__ == '__main__':
    app.run(port=3000, debug=True)