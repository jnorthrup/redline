#ifndef WALDO_H
#define WALDO_H

#include "robot.h"
#include <string>
#include <vector>
#include <memory>

class Waldo : public Robot {
public:
    Waldo() : Robot("Waldo", 6) {
        capabilities = {
            "Precision building",
            "Microsurgery",
            "Object manipulation",
            "Repair operations",
            "Delicate construction"
        };
        limitations = {
            "Limited to 1 meter height",
            "Requires microsurgery extension for complex tasks",
            "Energy-intensive operations"
        };
        
        personality = {
            "Highly precise and methodical",
            "Known for delicate operations",
            "Designed by Frobozz Engineering Company",
            "Six grasping extensions",
            "Specialized in microsurgery and repair",
            "Known for the phrase 'Precision is key'"
        };
    }

    void perform_task() override;
    void report_status() override;
    void describe_personality();
    
    // Specific Waldo functionality
    void perform_microsurgery();
    void build_structure();
    void repair_object();
    void install_extension();
    bool has_microsurgery_extension() const;
    void set_microsurgery_extension(bool status);

private:
    std::vector<std::string> personality;
    bool microsurgery_extension_installed = false;
    
    // Internal methods
    void check_extensions();
    void update_status();
};

#endif // WALDO_H
