#ifndef WALDO_H
#define WALDO_H

#include <string>
#include <vector>
#include <iostream>

class Waldo {
public:
    Waldo();
    
    void locate();
    void hide();
    void reveal();
    void report_position();
    void set_position(const std::string& position);
    std::string get_position() const;
    
private:
    std::string current_position = "unknown";
    std::vector<std::string> possible_locations = {
        "beach", "city", "forest", "mountain"
    };
};

#endif // WALDO_H
