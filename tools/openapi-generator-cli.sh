#!/bin/bash
# Define the URL and the target file
URL="https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.9.0/openapi-generator-cli-7.9.0.jar"
TARGET_FILE="openapi-generator-cli.jar"
TARGET_DIR="$(dirname "$0")"

# Check if the file already exists
if [ ! -f "$TARGET_DIR/$TARGET_FILE" ]; then
    echo "Downloading $TARGET_FILE..."
    wget $URL -O "$TARGET_DIR/$TARGET_FILE"
    if [ $? -ne 0 ]; then
        echo "Failed to download $TARGET_FILE"
        exit 1
    fi
    echo "$TARGET_FILE downloaded successfully."
else
    echo "$TARGET_FILE already exists."
fi

# Run the openapi-generator-cli
java -jar "$TARGET_DIR/$TARGET_FILE" "$@"
