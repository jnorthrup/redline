#ifndef SENSA_H
#define SENSA_H

#include "robot.h"
#include <string>
#include <vector>
#include <memory>

class Sensa : public Robot {
public:
    Sensa() : Robot("Sensa", 3) {
        capabilities = {
            "Energy flow detection",
            "Environmental monitoring",
            "Diagnostic analysis",
            "Abnormal activity detection",
            "Vibration analysis"
        };
        limitations = {
            "Limited to 1 meter height",
            "Delicate sensory extensions",
            "Requires calibration"
        };
        
        personality = {
            "Highly sensitive and analytical",
            "Known for precise diagnostics",
            "Designed by Frobozz Engineering Company",
            "Three sensory extensions",
            "Specialized in environmental monitoring",
            "Known for the phrase 'I sense something'"
        };
    }

    void perform_task() override;
    void report_status() override;
    void describe_personality();
    
    // Specific Sensa functionality
    void detect_energy_flow();
    void monitor_environment();
    void perform_diagnostic();
    void calibrate_sensors();
    bool is_calibrated() const;
    void set_calibrated(bool status);

private:
    std::vector<std::string> personality;
    bool calibrated = false;
    
    // Internal methods
    void check_sensors();
    void update_status();
};

#endif // SENSA_H
