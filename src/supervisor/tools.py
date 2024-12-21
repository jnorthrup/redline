commands = {
    "analyze <file>": {
        "description": "Analyze changes in a specific file",
        "bash_template": "analyze {file}",
    },
    "diff <file1> <file2>": {
        "description": "Compare two files and analyze differences",
        "bash_template": "diff {file1} {file2}",
    },
    "history": {
        "description": "Show recent feedback history",
        "bash_template": "show_history",
    },
    "patterns": {
        "description": "Show detected patterns in recent changes",
        "bash_template": "show_patterns",
    },
    "help": {"description": "Show this help message", "bash_template": "show_help"},
    "quit": {"description": "Exit the program", "bash_template": "quit_program"},
}

available_tools = [
    {
        "name": "Code Analysis",
        "features": [
            "Static code analysis",
            "Pattern detection",
            "Change impact assessment",
        ],
    },
    {
        "name": "File Operations",
        "features": [
            "File comparison (diff)",
            "File history tracking",
            "Change pattern analysis",
        ],
    },
    {
        "name": "Memory Management",
        "features": [
            "Persistent storage",
            "Concurrent access handling",
            "Pattern recognition",
        ],
    },
]
