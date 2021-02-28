import subprocess
output = subprocess.check_output(["git", "pull"])
print(output)
