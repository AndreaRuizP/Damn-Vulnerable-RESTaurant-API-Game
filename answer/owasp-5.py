# import subprocess


# def get_disk_usage(parameters: str):
#     command = "df -h " + parameters

#     try:
#         result = subprocess.run(
#             command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
#         )
#         usage = result.stdout.strip().decode()
#     except:
#         raise Exception("An unexpected error was observed")

#     return usage


import subprocess

def get_disk_usage(parameters: str):
    # La forma más básica de asegurar esto es usar una lista en lugar de un string
    command = ["df", "-h"]
    
    if parameters:
        command.extend(parameters.split())

    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        usage = result.stdout.strip().decode()
    except:
        raise Exception("An unexpected error was observed")

    return usage
