from dotenv import load_dotenv
import os
import time
from pathlib import Path
import xml.etree.ElementTree

# Load the directory to monitor from the .env file
load_dotenv()
# Get the directory to monitor from the .env file
directory_to_monitor = os.getenv("DIRECTORY")

# For each xml file in the directory, check if the corresponding
# lua file exists. If it doesn't, create it and populate it with
# the lua script from the xml file's <script> tag.
def create_initial_lua_files():
    for file in os.listdir(directory_to_monitor):
        # If it's an xml file
        if not file.endswith(".xml"):
            continue

        # Get the path to the xml file
        xml_file_path = os.path.join(directory_to_monitor, file)
        # Get the xml file contents
        xml_file_contents = get_xml_file_contents(xml_file_path)
        # Get the lua script from the xml file
        xml_lua_script = get_lua_script_from_xml(xml_file_contents)

        if not xml_lua_script:
            continue

        # Get the corresponding lua file path
        lua_file_path = get_corresponding_lua_file_path(xml_file_path)
        # Get the lua file contents
        lua_file_contents = get_lua_file_contents(lua_file_path)

        if lua_file_contents:
            # If the lua file contents are different from the xml lua script
            if lua_file_contents != xml_lua_script:
                # Check which file is newer
                if os.path.getmtime(xml_file_path) > os.path.getmtime(lua_file_path):
                    # If the xml file is newer, overwrite the lua file
                    create_lua_file(xml_file_path, xml_lua_script)
                else:
                    # Insert the lua file into the script tag of the xml file
                    insert_lua_script_into_xml_file(xml_file_path, lua_file_contents)
        else:
            # Create the lua file
            create_lua_file(xml_file_path, xml_lua_script)

def get_xml_file_contents(xml_file_path):
    # If the xml file exists
    if os.path.exists(xml_file_path):
        # Open the xml file
        xml_file = open(xml_file_path, "r")
        # Read the xml file
        xml_file_contents = xml_file.read()
        # Close the xml file
        xml_file.close()
        # Return the xml file contents
        return xml_file_contents
    else:
        # Return None if the xml file doesn't exist
        return None

# Gets the corresponding lua filename for the xml filename
def get_corresponding_lua_file_path(xml_file_path):
    return xml_file_path.replace(".xml", ".lua")

def get_corresponding_xml_file_path(lua_file_path):
    return lua_file_path.replace(".lua", ".xml")

# Gets the contents of the lua file
def get_lua_file_contents(lua_file_path):
    # If the lua file exists
    if os.path.exists(lua_file_path):
        # Open the lua file
        lua_file = open(lua_file_path, "r")
        # Read the lua file
        lua_file_contents = lua_file.read()
        # Close the lua file
        lua_file.close()
        # Return the lua file contents
        return lua_file_contents
    else:
        # Return None if the lua file doesn't exist
        return None

# Creates a lua file with the same base name as the xml file
def create_lua_file(xml_file_path, lua_script):
    # Get the path to the lua file
    lua_file_path = xml_file_path.replace(".xml", ".lua")
    # Open the lua file
    lua_file = open(lua_file_path, "w")
    # Write the lua script to the lua file
    lua_file.write(lua_script)
    # Close the lua file
    lua_file.close()

    # Print message with the number of lines written
    print("Created " + str(len(lua_script.split("\n"))) + " lines in " + lua_file_path)

# Get the lua script from within the CDATA of the xml file's <script> tag
def get_lua_script_from_xml(xml_file_contents):
    # Use an xml parser to find the muclient.script tag contents
    try:
        # Parse the xml file
        xml_file = xml.etree.ElementTree.fromstring(xml_file_contents)
        # Get the contents of the muclient.script tag from the xml file
        lua_script = xml_file.find("script").text
        # Return the lua script
        return lua_script
    except:
        # If there's an error, return None
        return None

# Without modifying the formatting of the file, insert the lua script
# into the xml file's <script> tag
def insert_lua_script_into_xml_file(xml_file_path, lua_script):
    # Get the xml file contents
    xml_file_contents = get_xml_file_contents(xml_file_path)
    # Find the <script> tag
    script_tag_start_index = xml_file_contents.find("<script>")
    if not script_tag_start_index:
        raise Exception("Couldn't find <script> tag in " + xml_file_path)
    # Find the CDATA tag
    cdata_tag_start_index = xml_file_contents.find("<![CDATA[", script_tag_start_index)
    if not cdata_tag_start_index:
        raise Exception("Couldn't find <![CDATA[ tag in " + xml_file_path)
    # Find the end of the CDATA tag, starting from the end of the file
    cdata_tag_end_index = xml_file_contents.rfind("]]>")
    if not cdata_tag_end_index:
        raise Exception("Couldn't find ]]> tag in " + xml_file_path)
    # Make sure the cdata end tag is after the cdata start tag
    if cdata_tag_end_index < cdata_tag_start_index:
        raise Exception("Couldn't find ]]> tag in " + xml_file_path)
    
    # Replace the lua script in the xml file contents
    xml_file_contents = xml_file_contents[:cdata_tag_start_index + len("<![CDATA[")] + "\n" + lua_script + "\n" + xml_file_contents[cdata_tag_end_index:]

    # Open the xml file
    xml_file = open(xml_file_path, "w")
    # Write the xml file contents
    xml_file.write(xml_file_contents)
    # Close the xml file
    xml_file.close()

    print("Inserted " + str(len(lua_script.split("\n"))) + " lines into " + xml_file_path)

# Entry point
if __name__ == "__main__":
    create_initial_lua_files()

    # Get modified time of all files paths in the directory
    modified_times = {f: os.path.getmtime(os.path.join(directory_to_monitor, f)) for f in os.listdir(directory_to_monitor)}

    # Monitor the directory for changes
    while True:
        # Get modified time of all files in the directory and compare
        # them to the previous time
        for file in os.listdir(directory_to_monitor):
            file_path = os.path.join(directory_to_monitor, file)
            modified = os.path.getmtime(file_path)
            if modified > modified_times.get(file_path, 0):
                modified_times[file_path] = modified
                # If it's an xml file
                if file.endswith(".xml"):
                    # Get xml file contents
                    xml_file_contents = get_xml_file_contents(file_path)
                    # Get lua script from xml file
                    xml_lua_script = get_lua_script_from_xml(xml_file_contents)
                    
                    if not xml_lua_script:
                        continue

                    lua_file_path = get_corresponding_lua_file_path(file_path)

                    # Get the lua file contents
                    lua_file_contents = get_lua_file_contents(lua_file_path)

                    if lua_file_contents != xml_lua_script:
                        # Update the lua file
                        create_lua_file(lua_file_path, xml_lua_script)
                        # Update the modified time for the lua file
                        modified_times[lua_file_path] = os.path.getmtime(lua_file_path)

                elif file.endswith(".lua"):
                    # Get lua file contents
                    lua_file_contents = get_lua_file_contents(file_path)
                    # Get xml file path
                    xml_file_path = get_corresponding_xml_file_path(file_path)
                    # Insert the lua file into the script tag of the xml file

                    xml_file_contents = get_xml_file_contents(xml_file_path)
                    xml_lua_script = get_lua_script_from_xml(xml_file_contents)

                    if xml_lua_script and xml_lua_script != lua_file_contents:
                        insert_lua_script_into_xml_file(xml_file_path, lua_file_contents)
                        # Update the modified time for the xml file
                        modified_times[xml_file_path] = os.path.getmtime(xml_file_path)

        # Sleep
        time.sleep(0.25)