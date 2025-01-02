#ifndef IRIS_H
#define IRIS_H

#include <string>
#include <vector>
#include <iostream>

class Iris {
public:
    Iris();
    
    void perform_task();
    void report_status();
    void describe_personality();
    void scan_environment();
    void transmit_visual_data();
    void access_maintenance_panel();
    void request_repair();
    bool is_functional() const;
    void set_functional(bool status);
    
private:
    void check_visual_systems();
    void update_status();
    
    bool functional = true;
    bool maintenance_panel_accessible = false;
    std::vector<std::string> personality = {
        "Observant",
        "Detail-oriented", 
        "Visual thinker",
        "Systematic"
    };
};

#endif // IRIS_H
