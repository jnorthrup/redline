# Asset Management Convention

This document outlines a convention for managing project assets, including those not directly managed by CMake.

## 1. Scripts (Python, Scheme, Shell)

*   Place all scripts in a dedicated `scripts/` directory at the top level.
*   Use CMake's `add_custom_command` and `add_custom_target` to execute these scripts as part of the build process, if needed. For example, scripts that generate code or configuration files.
*   For scripts that are not part of the build process, document their purpose and usage in the `README.md`.

## 2. Documentation (Markdown)

*   Keep documentation files in the `charter/` directory or a dedicated `docs/` directory.
*   Use CMake to copy these files to the build directory if needed for distribution.
*   Consider using a documentation generator (e.g., Sphinx) if the documentation becomes more complex.

## 3. Configuration Templates

*   Keep configuration templates in the `templates/` directory.
*   Use CMake to process these templates during the build process, replacing placeholders with actual values.
*   Use a consistent naming convention for template files (e.g., `*.config.in`).

## 4. Tools

*   Keep tools in the `tools/` directory.
*   If tools are used as part of the build process, use CMake to execute them.
*   Document the purpose and usage of each tool in the `README.md`.

## 5. Patches

*   Keep patches in the `patches/` directory.
*   Use CMake to apply these patches during the build process.

## 6. Work Queue Data

*   Keep work queue data in the `work_queue/` directory.
*   Document the structure and purpose of this data in the `README.md`.

## 7. Mixer Files

*   Keep mixer files in the `mixer/` directory.
*   Use CMake to process these files during the build process.

## 8. Temporary Files

*   Temporary files (e.g., `*.txt`, `*.log`) should be generated in a dedicated `build/tmp/` directory.
*   These files should be excluded from version control using `.gitignore`.

## 9. Other Files

*   Any other files that are not part of the core project should be placed in a dedicated directory (e.g., `assets/`) and managed appropriately.