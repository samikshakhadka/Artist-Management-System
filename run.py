import os
import sys
import argparse
import importlib
import subprocess

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Artist Management System')
    parser.add_argument('command', nargs='+', help='Command to run')
    return parser.parse_args()

def setup_client_files():
    """Set up static files and HTML templates"""
    print("📂 Setting up client files...")
    
    # Create directory structure if it doesn't exist
    os.makedirs('client/css', exist_ok=True)
    os.makedirs('client/js', exist_ok=True)
    os.makedirs('client/static', exist_ok=True)
    
    # Copy login and registration templates
    if os.path.exists('login-html.html'):
        with open('client/login.html', 'w') as f:
            with open('login-html.html', 'r') as source:
                f.write(source.read())
        print("✅ Created login.html")
    
    if os.path.exists('register-html.html'):
        with open('client/register.html', 'w') as f:
            with open('register-html.html', 'r') as source:
                f.write(source.read())
        print("✅ Created register.html")
    
    # Copy CSS file
    if os.path.exists('css-styles.css'):
        with open('client/css/styles.css', 'w') as f:
            with open('css-styles.css', 'r') as source:
                f.write(source.read())
        print("✅ Created styles.css")
    
    # Copy JS file
    if os.path.exists('auth-js.js'):
        with open('client/js/auth.js', 'w') as f:
            with open('auth-js.js', 'r') as source:
                f.write(source.read())
        print("✅ Created auth.js")

def run_project():
    """Start the web server and set up everything needed"""
    # Set up client files
    setup_client_files()
    
    print("🚀 Starting Artist Management System...")
    
    # Check multiple possible locations for server.py
    possible_locations = [
        'server.py',                     # Current directory
        'server/server.py',              # In server subdirectory
        './server/server.py',            # Explicit relative path
        os.path.join('server', 'server.py')  # Using path join
    ]
    
    server_file = None
    for location in possible_locations:
        if os.path.exists(location):
            server_file = location
            print(f"✅ Found server.py at: {location}")
            break
    
    if server_file:
        # Get the directory containing server.py
        server_dir = os.path.dirname(server_file)
        if not server_dir:
            server_dir = '.'
        
        # Create a simple wrapper file to import and run the server
        with open('_temp_run_server.py', 'w') as f:
            f.write(f"""
# Temporary wrapper to run the server
import os
import sys

# Add the server directory to the path
sys.path.append(os.path.abspath('{server_dir}'))

# If it's in a subdirectory, add parent directory too
if '{server_dir}' != '.':
    sys.path.append(os.path.abspath('.'))

try:
    # Try different import approaches
    try:
        from server import run_server
        print("Imported server from module")
    except ImportError:
        # If in a subdirectory, try importing with the directory name
        if '{server_dir}' != '.':
            module_name = '{server_dir}'.replace('/', '.').strip('.')
            exec(f"from {{module_name}}.server import run_server")
            print(f"Imported server from {{module_name}}.server")
        else:
            raise ImportError("Could not import server module")
    
    # Run the server
    print("Starting the server...")
    run_server()
except Exception as e:
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
""")
        
        try:
            # Run the wrapper script as a subprocess
            print("Starting server...")
            subprocess.call([sys.executable, '_temp_run_server.py'])
        except Exception as e:
            print(f"❌ Error running server: {str(e)}")
            sys.exit(1)
        finally:
            # Clean up the temporary file
            if os.path.exists('_temp_run_server.py'):
                os.remove('_temp_run_server.py')
    else:
        # Last resort: try direct execution of the server.py file
        print("🔍 Could not find server.py in standard locations.")
        print("Please specify the path to your server.py file:")
        server_path = input("> ")
        
        if os.path.exists(server_path):
            print(f"✅ Using server at: {server_path}")
            try:
                # Get the directory containing server.py
                server_dir = os.path.dirname(server_path)
                if not server_dir:
                    server_dir = '.'
                
                # Create a simple wrapper file
                with open('_temp_run_server.py', 'w') as f:
                    f.write(f"""
# Temporary wrapper to run the server
import os
import sys
import importlib.util

# Add paths
sys.path.append(os.path.abspath('{server_dir}'))
sys.path.append(os.path.abspath('.'))

# Load the module from file path
spec = importlib.util.spec_from_file_location("server_module", "{server_path}")
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

# Run the server
print("Starting the server...")
server_module.run_server()
""")
                
                # Run the wrapper script
                subprocess.call([sys.executable, '_temp_run_server.py'])
            except Exception as e:
                print(f"❌ Error running server: {str(e)}")
                sys.exit(1)
            finally:
                # Clean up
                if os.path.exists('_temp_run_server.py'):
                    os.remove('_temp_run_server.py')
        else:
            print(f"❌ File not found: {server_path}")
            sys.exit(1)

def main():
    """Main entry point for the command runner"""
    args = parse_args()
    
    if len(args.command) >= 2 and args.command[0] == 'run' and args.command[1] == 'project':
        print("=" * 60)
        print("  Artist Management System - Project Runner")
        print("=" * 60)
        
        # Run the project
        run_project()
    else:
        print(f"❌ Unknown command: {' '.join(args.command)}")
        print("Available commands:")
        print("  run project - Start the Artist Management System")
        sys.exit(1)

if __name__ == "__main__":
    main()