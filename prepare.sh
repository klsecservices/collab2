#!/bin/bash

# Generate password file for nginx authentication
echo "Generating password file for nginx authentication..."
echo "Username: "
read username

htpasswd -c ./passwd $username

echo "Updating static files..."
cd collab-front; ./update_static.sh; cd ..
cd collab-agent; ./build.sh; cd ..
