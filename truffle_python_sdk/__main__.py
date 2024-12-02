import sys
import importlib
import argparse
import inspect
from truffle_python_sdk import TruffleApp

def main():
    parser = argparse.ArgumentParser(
        description="Truffle CLI - Run your Truffle applications."
    )
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # Sub-command for running the app in REST mode
    parser_run_rest = subparsers.add_parser('run:rest', help='Run the app in REST mode')
    parser_run_rest.add_argument('module', help='The application module to run')
    parser_run_rest.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser_run_rest.add_argument('--port', type=int, default=None, help='Port number')
    parser_run_rest.add_argument('--log-level', type=str, default='info', help='Logging level')
    parser_run_rest.add_argument('--reload', action='store_true', help='Enable auto-reload')

    # Sub-command for running the app in gRPC mode
    parser_run_grpc = subparsers.add_parser('run:grpc', help='Run the app in gRPC mode')
    parser_run_grpc.add_argument('module', help='The application module to run')
    parser_run_grpc.add_argument('--host', type=str, default='0.0.0.0', help='Host address')
    parser_run_grpc.add_argument('--port', type=int, default=None, help='Port number')
    parser_run_grpc.add_argument('--log-level', type=str, default='info', help='Logging level')

    # Sub-command for generating the .proto files
    parser_proto = subparsers.add_parser('proto', help='Generate .proto files without starting a server')
    parser_proto.add_argument('module', help='The application module to generate .proto files from')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Import the specified module
    module_name = args.module.replace('.py', '').replace('/', '.').replace('\\', '.')
    try:
        app_module = importlib.import_module(module_name)
    except ImportError as e:
        print(f"Cannot import module '{module_name}': {e}")
        sys.exit(1)

    # Find the first TruffleApp instance in the module
    app = None
    for name, obj in inspect.getmembers(app_module):
        if isinstance(obj, TruffleApp):
            app = obj
            break

    if app is None:
        print(f"No instance of TruffleApp found in module '{module_name}'.")
        sys.exit(1)

    # Handle the sub-commands
    if args.command == 'run:rest':
        app.start(
            mode='rest',
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload
        )
    elif args.command == 'run:grpc':
        app.start(
            mode='grpc',
            host=args.host,
            port=args.port,
            log_level=args.log_level
        )
    elif args.command == 'proto':
        app.generate_proto_files()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
