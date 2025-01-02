#ifndef IRIS_H
#define IRIS_H

#include "robot.h"
#include <string>
#include <vector>
#include <memory>

class Iris : public Robot {
public:
    Iris() : Robot("Iris", 2) {
        capabilities = {
            "High-resolution visual scanning",
            "Environment mapping",
            "Object identification",
            "Maintenance panel access",
            "Visual data transmission"
        };
        limitations = {
            "Limited to 1 meter height",
            "Vulnerable to visual damage",
            "Requires repair for full functionality"
        };
        
        personality = {
            "Delicate and precise",
            "Known for high-quality visual data",
            "Maintenance panel accessible to authorized robots",
            "Designed by Frobozz Engineering Company",
            "Only two grasping extensions",
            "Limited to mapped areas of the Complex",
            "Known for the phrase 'The eyes have it'"
        };
    }

    void perform_task() override;
    void report_status() override;
    void describe_personality();
    
    // Specific Iris functionality
    void scan_environment();
    void transmit_visual_data();
    void access_maintenance_panel();
    void request_repair();
    bool is_functional() const;
    void set_functional(bool status);

private:
    std::vector<std::string> personality;
    bool functional = true;
    bool maintenance_panel_accessible = false;
    
    // Internal methods
    void check_visual_systems();
    void update_status();
};

#endif // IRIS_H
