from quick_and_dirty_grpc_wrapper_scrapper import fn, start_grpc_server_from_python_script

@fn
def echo(message):
    return message

# @fn adds .__is_exposed__ attribute to the function