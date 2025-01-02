#include "iris.h"
#include <iostream>

void Iris::perform_task() {
    if (!functional) {
        std::cout << "Iris: Unable to perform tasks - visual systems offline\n";
        return;
    }
    
    scan_environment();
    transmit_visual_data();
    update_status();
}

void Iris::report_status() {
    std::cout << "Iris Status Report:\n";
    std::cout << " - Functional: " << (functional ? "Yes" : "No") << "\n";
    std::cout << " - Maintenance Panel: " 
              << (maintenance_panel_accessible ? "Accessible" : "Locked") << "\n";
    check_visual_systems();
}

void Iris::describe_personality() {
    std::cout << "Iris Personality Traits:\n";
    for (const auto& trait : personality) {
        std::cout << " - " << trait << "\n";
    }
}

void Iris::scan_environment() {
    if (functional) {
        std::cout << "Iris: Scanning environment with high-resolution visual sensors\n";
        // Implementation of scanning logic
    } else {
        std::cout << "Iris: Visual scanners offline - unable to scan\n";
    }
}

void Iris::transmit_visual_data() {
    if (functional) {
        std::cout << "Iris: Transmitting visual data to FC\n";
        // Implementation of data transmission
    } else {
        std::cout << "Iris: Unable to transmit data - systems offline\n";
    }
}

void Iris::access_maintenance_panel() {
    if (maintenance_panel_accessible) {
        std::cout << "Iris: Accessing maintenance panel\n";
        // Implementation of maintenance panel access
    } else {
        std::cout << "Iris: Maintenance panel not accessible\n";
    }
}

void Iris::request_repair() {
    if (!functional) {
        std::cout << "Iris: Requesting repair for visual systems\n";
        // Implementation of repair request
    } else {
        std::cout << "Iris: Systems functional - no repair needed\n";
    }
}

bool Iris::is_functional() const {
    return functional;
}

void Iris::set_functional(bool status) {
    functional = status;
    std::cout << "Iris: Functional status set to " 
              << (status ? "online" : "offline") << "\n";
}

void Iris::check_visual_systems() {
    if (functional) {
        std::cout << "Iris: Visual systems operational\n";
    } else {
        std::cout << "Iris: Visual systems require repair\n";
    }
}

void Iris::update_status() {
    // Implementation of status update logic
    std::cout << "Iris: Status updated\n";
}
