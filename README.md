# Project Title

<!-- ...existing content... -->

## Resolving CMake Generator Mismatch and FetchContent Error

Follow these steps to resolve issues related to CMake generator mismatch and FetchContent error:

1. **Remove Existing CMake Cache and Files:**

    ```bash
    rm -rf CMakeCache.txt CMakeFiles
    ```

2. **Ensure Ninja is Installed:**

    ```bash
    brew install ninja
    ```

3. **Reconfigure CMake with the Ninja Generator:**

    ```bash
    cmake -G Ninja ..
    ```

4. **Build the Project:**

    ```bash
    ninja
    ```

<!-- ...existing content... -->
