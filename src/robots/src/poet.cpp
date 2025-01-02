#include "poet.h"
#include <iostream>

Poet::Poet() {
    current_inspiration = "nature";
}

void Poet::compose_poem() {
    std::cout << "Poet: Composing poem inspired by " << current_inspiration << "\n";
    // Implementation of poem composition logic
}

void Poet::recite_poem() {
    std::cout << "Poet: Reciting poem\n";
    // Implementation of poem recitation logic
}

void Poet::set_inspiration(const std::string& inspiration) {
    current_inspiration = inspiration;
    std::cout << "Poet: Inspiration set to " << inspiration << "\n";
}

std::string Poet::get_inspiration() const {
    return current_inspiration;
}
