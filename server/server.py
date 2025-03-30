import json
import http.server
import socketserver
import urllib.parse
from http import cookies
import cgi
import os
import re
import datetime 
from auth.auth_handler import login, register, destroy_session, validate_session, get_user_from_session
from controllers.controller_init import register_all_routes



class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)
    


# Configuration
PORT = 8000
HOST = "localhost"

# Dictionary to store route handlers
routes = {}

# Utility function to parse cookies
def parse_cookies(cookie_string):
    cookie = cookies.SimpleCookie()
    cookie.load(cookie_string)
    return {key: morsel.value for key, morsel in cookie.items()}

# Utility function to parse query parameters
def parse_query_params(query_string):
    return {k: v[0] for k, v in urllib.parse.parse_qs(query_string).items()}

# Utility function to parse JSON body
def parse_json_body(request_handler):
    content_length = int(request_handler.headers.get('Content-Length', 0))
    if content_length == 0:
        return {}
    
    body = request_handler.rfile.read(content_length)
    try:
        return json.loads(body.decode('utf-8'))
    except json.JSONDecodeError:
        return {}

# Utility function to parse form data
def parse_form_data(request_handler):
    content_type = request_handler.headers.get('Content-Type', '')
    if 'multipart/form-data' in content_type:
        form = cgi.FieldStorage(
            fp=request_handler.rfile,
            headers=request_handler.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        data = {}
        for field in form.keys():
            if form[field].filename:
                # Handle file upload
                data[field] = {
                    'filename': form[field].filename,
                    'value': form[field].value
                }
            else:
                data[field] = form[field].value
        return data
    else:
        content_length = int(request_handler.headers.get('Content-Length', 0))
        post_data = request_handler.rfile.read(content_length).decode('utf-8')
        return {k: v[0] for k, v in urllib.parse.parse_qs(post_data).items()}

# Route decorator
def route(path, methods=None):
    if methods is None:
        methods = ['GET']
    
    def decorator(func):
        for method in methods:
            # Check if path contains parameters like {id}
            if '{' in path:
                # Convert to regex pattern
                pattern = path.replace('{', '(?P<').replace('}', '>[^/]+)')
                routes[(method.upper(), re.compile(pattern))] = func
            else:
                routes[(method.upper(), path)] = func
        return func
    
    return decorator

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')
    
    def handle_request(self, method):
        # Parse URL path and query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = parse_query_params(parsed_url.query)
        
        # Parse cookies
        cookies_string = self.headers.get('Cookie', '')
        self.cookies = parse_cookies(cookies_string)
        
        # Create request object to pass to route handlers
        self.request = type('Request', (), {
            'method': method,
            'path': path,
            'query_params': query_params,
            'cookies': self.cookies,
            'headers': self.headers,
            'form_data': {},
            'json_data': {},
            'user': None
        })
        
        # Parse request body based on content type
        if method in ['POST', 'PUT']:
            content_type = self.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                self.request.json_data = parse_json_body(self)
            else:
                self.request.form_data = parse_form_data(self)
        
        # Check for static file requests
        if path.startswith('/static/'):
            return self.serve_static_file(path)
        
        # Check for session and set user if authenticated
        session_id = self.cookies.get('session_id')
        if session_id:
            self.request.user = get_user_from_session(session_id)
        
        # Find matching route handler
        handler = self.find_route_handler(method, path)
        
        if handler:
            # Execute the route handler
            try:
                result = handler(self.request)
                self.send_response(result.get('status', 200))
                
                # Set cookies if needed
                if 'cookies' in result:
                    for name, value in result['cookies'].items():
                        cookie = cookies.SimpleCookie()
                        cookie[name] = value
                        self.send_header('Set-Cookie', cookie[name].OutputString())
                
                # Set headers if needed
                if 'headers' in result:
                    for name, value in result['headers'].items():
                        self.send_header(name, value)
                
                # Set content type
                self.send_header('Content-type', result.get('content_type', 'application/json'))
                self.end_headers()
                
                # Send response body
                if 'body' in result:
                    if isinstance(result['body'], str):
                        self.wfile.write(result['body'].encode('utf-8'))
                    elif isinstance(result['body'], bytes):
                        self.wfile.write(result['body'])
                    else:
                        self.wfile.write(json.dumps(result['body'],cls=DateTimeEncoder).encode('utf-8'))
            except Exception as e:
                print(f"Error handling request: {e}")
                self.send_error(500, str(e))
        else:
            # Check if it's an HTML file
            if path.endswith('.html') or path == '/':
                return self.serve_html_file(path)
            
            # Route not found
            self.send_error(404, "Route not found")
    
    def find_route_handler(self, method, path):
        # First check for exact matches
        exact_match = routes.get((method, path))
        if exact_match:
            return exact_match
        
        # Then check for regex pattern matches
        for (route_method, route_path), handler in routes.items():
            if route_method != method:
                continue
            
            if isinstance(route_path, re.Pattern):
                match = route_path.fullmatch(path)
                if match:
                    # Add captured parameters to request
                    self.request.path_params = match.groupdict()
                    return handler
        
        return None
    
    def serve_static_file(self, path):
        # Strip off the /static/ prefix
        file_path = path[8:]
        
        # Determine the file's full path
        full_path = os.path.join('client', 'static', file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            # Determine content type based on file extension
            _, ext = os.path.splitext(full_path)
            content_types = {
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml'
            }
            content_type = content_types.get(ext.lower(), 'application/octet-stream')
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            
            with open(full_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, "File not found")
    
    def serve_html_file(self, path):
        # If root path, serve index.html
        if path == '/':
            file_path = 'index.html'
        else:
            # Strip off the leading slash
            file_path = path[1:]
        
        # Determine the file's full path
        full_path = os.path.join('client', file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open(full_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, "File not found")

# Define authentication routes
@route('/api/login', methods=['POST'])
def api_login(request):
    data = request.json_data or request.form_data
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return {
            'status': 400,
            'body': {'success': False, 'message': 'Email and password are required'}
        }
    
    auth_result = login(email, password)
    
    if auth_result:
        return {
            'status': 200,
            'cookies': {'session_id': auth_result['session_id']},
            'body': {
                'success': True,
                'message': 'Login successful',
                'user': auth_result['user']
            }
        }
    else:
        return {
            'status': 401,
            'body': {'success': False, 'message': 'Invalid email or password'}
        }

@route('/api/register', methods=['POST'])
def api_register(request):
    data = request.json_data or request.form_data
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    
    if not first_name or not last_name or not email or not password:
        return {
            'status': 400,
            'body': {'success': False, 'message': 'All fields are required'}
        }
    
    result = register(first_name, last_name, email, password)
    
    return {
        'status': 201 if result['success'] else 400,
        'body': result
    }

@route('/api/logout', methods=['POST'])
def api_logout(request):
    session_id = request.cookies.get('session_id')
    
    if session_id:
        destroy_session(session_id)
    
    return {
        'status': 200,
        'cookies': {'session_id': ''},
        'body': {'success': True, 'message': 'Logout successful'}
    }

@route('/api/check-auth', methods=['GET'])
def api_check_auth(request):
    session_id = request.cookies.get('session_id')
    
    if not session_id:
        return {
            'status': 401,
            'body': {'authenticated': False}
        }
    
    session = validate_session(session_id)
    if not session:
        return {
            'status': 401,
            'body': {'authenticated': False}
        }
    
    user = get_user_from_session(session_id)
    
    return {
        'status': 200,
        'body': {
            'authenticated': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role']
            }
        }
    }

# Register all routes
register_all_routes(route)

# Start the server
def run_server():
    # Create the directory structure if it doesn't exist
    os.makedirs('client/static', exist_ok=True)
    
    print(f"Starting server at http://{HOST}:{PORT}")
    httpd = socketserver.TCPServer((HOST, PORT), RequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()