#include "waldo.h"
#include <iostream>

Waldo::Waldo() {
    current_position = "unknown";
}

void Waldo::locate() {
    std::cout << "Waldo: Searching for target location\n";
    // Implementation of location logic
}

void Waldo::hide() {
    std::cout << "Waldo: Hiding in current location\n";
    current_position = "hidden";
}

void Waldo::reveal() {
    std::cout << "Waldo: Revealing current location\n";
    current_position = "visible";
}

void Waldo::report_position() {
    std::cout << "Waldo's current position: " << current_position << "\n";
}

void Waldo::set_position(const std::string& position) {
    current_position = position;
    std::cout << "Waldo: Position set to " << position << "\n";
}

std::string Waldo::get_position() const {
    return current_position;
}
