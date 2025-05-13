import os
import re

def parse_jar_name_and_version(jar_path):
    """
    Extract the main name and version from a JAR file path.
    :param jar_path: Full path to the JAR file.
    :return: Tuple (name, version) or (name, None) if version is not found.
    """
    jar_name = jar_path.split("/")[-1]  # Extract the file name
    parts = jar_name.split("-")
    if len(parts) > 1 and parts[-1].endswith(".jar"):
        # slf4j-reload4j-1.7.36.jar
        version = parts[-1][:-4]  # Extract version (without .jar)
        name = "-".join(parts[:-1])
        return {'base_name':name, 'version':version, 'jar_name': jar_name}
    return {'base_name':jar_name, 'version': '', 'jar_name': jar_name}

def parse_jar_name(filename):
    p = parse_jar_name_and_version(filename)
    return p.get('base_name')


docker_jars_path = "docker_jars"
package_jars_path = "package_jars"
print(f'grooming the package jars to avoid conflicts with the jars already in the spark base image.')
docker_jar_names = {(parse_jar_name(f), f) for f in os.listdir(docker_jars_path) if f.endswith('.jar')}

for f in os.listdir(package_jars_path):
    if f.endswith(".jar"):
        package_parsed = parse_jar_name_and_version(f)
        package_base_name = package_parsed.get('base_name')
        package_file_name = package_parsed.get('jar_name')
        for docker_base_name, docker_file_name in docker_jar_names:
            if docker_base_name and package_base_name and docker_base_name == package_base_name:
                package_file_path = os.path.join(package_jars_path, f)
                print(f"Removing {package_base_name} from package_jars (conflicts with docker jars): package: {package_file_name}, docker: {docker_file_name}")
                os.remove(package_file_path)
