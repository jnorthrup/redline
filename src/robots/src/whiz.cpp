#include "whiz.h"
#include <iostream>

Whiz::Whiz() {
    complexity_level = 1;
}

void Whiz::perform_calculation() {
    std::cout << "Whiz: Performing calculation at complexity level " << complexity_level << "\n";
    // Implementation of calculation logic
}

void Whiz::solve_problem() {
    std::cout << "Whiz: Solving problem at complexity level " << complexity_level << "\n";
    // Implementation of problem solving logic
}

void Whiz::set_complexity(int level) {
    complexity_level = level;
    std::cout << "Whiz: Complexity level set to " << level << "\n";
}

int Whiz::get_complexity() const {
    return complexity_level;
}
