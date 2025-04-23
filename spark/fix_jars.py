import os
import re


def parse_jar_name(filename):
    match = re.match(r"(.+?)-([\d.]+)\.jar$", filename)
    if match:
        return match.group(1)
    return None


docker_jars_path = "docker_jars"
package_jars_path = "package_jars"
print(f'grooming the package jars to avoid conflicts with the jars already in the spark base image.')
docker_jar_names = {parse_jar_name(f) for f in os.listdir(docker_jars_path) if f.endswith('.jar')}

for f in os.listdir(package_jars_path):
    if f.endswith(".jar") and parse_jar_name(f) in docker_jar_names:
        print(f"Removing {f} from package_jars (conflicts with Spark core)")
        os.remove(os.path.join(package_jars_path, f))
