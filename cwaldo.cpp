#include "cwaldo.h"
#include <iostream>

void CWaldo::perform_task() {
    std::cout << "CWaldo is manipulating objects with precision\n";
}

void CWaldo::report_status() {
    std::cout << "CWaldo status: Active, 6 graspers operational\n";
}

void CWaldo::describe_personality() {
    std::cout << "CWaldo personality traits:\n";
    for (const auto& trait : personality) {
        std::cout << " - " << trait << "\n";
    }
}
