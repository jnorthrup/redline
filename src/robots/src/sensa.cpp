#include "sensa.h"
#include <iostream>

Sensa::Sensa() {
    sensitivity_level = 5;
}

void Sensa::analyze_environment() {
    std::cout << "Sensa: Analyzing environment with sensitivity level " << sensitivity_level << "\n";
    // Implementation of environment analysis logic
}

void Sensa::report_findings() {
    std::cout << "Sensa's current findings:\n";
    std::cout << " - Sensitivity level: " << sensitivity_level << "\n";
}

void Sensa::set_sensitivity_level(int level) {
    sensitivity_level = level;
    std::cout << "Sensa: Sensitivity level set to " << level << "\n";
}

int Sensa::get_sensitivity_level() const {
    return sensitivity_level;
}
