from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import json

app = Flask(__name__)
CORS(app)  # Povolí CORS pro všechny požadavky

# Nastavení logování
logging.basicConfig(filename='proxy_error.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

@app.route('/api/proxy/grok', methods=['OPTIONS'])
def proxy_grok_options():
    resp = jsonify({'status': 'ok'})
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    logging.debug('Handled OPTIONS request for /api/proxy/grok')
    return resp, 200

@app.route('/api/proxy/grok', methods=['POST'])
def proxy_grok():
    try:
        data = request.get_json()
        if not data:
            error_msg = 'No JSON data received'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 400

        prompt = data.get('prompt')
        max_tokens = data.get('max_tokens')
        temperature = data.get('temperature')
        api_key = data.get('apiKey')

        if not all([prompt, max_tokens, temperature, api_key]):
            error_msg = 'Missing required parameters: ' + ', '.join([k for k, v in {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature, 'apiKey': api_key}.items() if not v])
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 400

        logging.debug(f'Received POST request: prompt={prompt}, max_tokens={max_tokens}, temperature={temperature}')

        try:
            # Zkus první: /v1/grok/chat s input formátem
            response = requests.post(
                'https://api.x.ai/v1/grok/chat',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                json={
                    'input': prompt,
                    'max_tokens': max_tokens,
                    'temperature': temperature
                }
            )
            response.raise_for_status()
            response_data = response.json()
            logging.debug(f'Response from xAI API (/grok/chat): {response_data}')
            if not response_data.get('choices') or not response_data['choices'][0].get('message', {}).get('content'):
                logging.error('Empty content in response from /grok/chat')
                return jsonify({'error': 'Empty content from xAI API (/grok/chat)'}), 500
            resp = jsonify(response_data)
            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return resp
        except requests.RequestException as e:
            logging.error(f'Proxy error with /grok/chat JSON: {str(e)}')
            try:
                # Zkus druhý: /v1/api/grok s input formátem
                response = requests.post(
                    'https://api.x.ai/v1/api/grok',
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {api_key}'
                    },
                    json={
                        'input': prompt,
                        'max_tokens': max_tokens,
                        'temperature': temperature
                    }
                )
                response.raise_for_status()
                response_data = response.json()
                logging.debug(f'Response from xAI API (/api/grok): {response_data}')
                if not response_data.get('choices') or not response_data['choices'][0].get('message', {}).get('content'):
                    logging.error('Empty content in response from /api/grok')
                    return jsonify({'error': 'Empty content from xAI API (/api/grok)'}), 500
                resp = jsonify(response_data)
                resp.headers.add('Access-Control-Allow-Origin', '*')
                resp.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
                resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                return resp
            except requests.RequestException as e2:
                logging.error(f'Proxy error with /api/grok JSON: {str(e2)}')
                try:
                    # Zkus třetí: /v1/chat/completions s OpenAI-style formátem
                    response = requests.post(
                        'https://api.x.ai/v1/chat/completions',
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {api_key}'
                        },
                        json={
                            'messages': [{'role': 'user', 'content': prompt}],
                            'max_tokens': max_tokens,
                            'temperature': temperature
                        }
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    logging.debug(f'Response from xAI API (/chat/completions): {response_data}')
                    if not response_data.get('choices') or not response_data['choices'][0].get('message', {}).get('content'):
                        logging.error('Empty content in response from /chat/completions')
                        return jsonify({'error': 'Empty content from xAI API (/chat/completions)'}), 500
                    resp = jsonify(response_data)
                    resp.headers.add('Access-Control-Allow-Origin', '*')
                    resp.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
                    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                    return resp
                except requests.RequestException as e3:
                    logging.error(f'Proxy error with /chat/completions JSON: {str(e3)}')
                    try:
                        # Zkus čtvrtý: /v1/completions s prompt formátem
                        response = requests.post(
                            'https://api.x.ai/v1/completions',
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {api_key}'
                            },
                            json={
                                'prompt': prompt,
                                'max_tokens': max_tokens,
                                'temperature': temperature
                            }
                        )
                        response.raise_for_status()
                        response_data = response.json()
                        logging.debug(f'Response from xAI API (/completions): {response_data}')
                        if not response_data.get('choices') or not response_data['choices'][0].get('message', {}).get('content'):
                            logging.error('Empty content in response from /completions')
                            return jsonify({'error': 'Empty content from xAI API (/completions)'}), 500
                        resp = jsonify(response_data)
                        resp.headers.add('Access-Control-Allow-Origin', '*')
                        resp.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
                        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                        return resp
                    except requests.RequestException as e4:
                        error_msg = f'Proxy error: /grok/chat failed ({str(e)}), /api/grok failed ({str(e2)}), /chat/completions failed ({str(e3)}), /completions failed ({str(e4)})'
                        logging.error(error_msg)
                        return jsonify({'error': error_msg}), 500
    except json.JSONDecodeError as e:
        error_msg = f'Failed to decode JSON object: {str(e)}'
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 400

if __name__ == '__main__':
    app.run(port=3000, debug=True)