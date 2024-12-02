import sys
import importlib

def main():
    if len(sys.argv) < 3 or sys.argv[1] != 'run':
        print("Usage: python truffle run <app>")
        sys.exit(1)

    app_path = sys.argv[2]
    module_name = app_path.replace('.py', '').replace('/', '.').replace('\\', '.')

    try:
        app_module = importlib.import_module(module_name)
    except ImportError as e:
        print(f"Cannot import module '{module_name}': {e}")
        sys.exit(1)

    if hasattr(app_module, 'app'):
        app = app_module.app
    else:
        print(f"The module '{module_name}' does not have an 'app' variable")
        sys.exit(1)

    app.start()

if __name__ == "__main__":
    main()
