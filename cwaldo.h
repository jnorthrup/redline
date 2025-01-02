#ifndef CWALDO_H
#define CWALDO_H

#include "robot.h"
#include <string>
#include <vector>

class CWaldo : public Robot {
public:
    CWaldo() : Robot("CWaldo", 6) {
        capabilities = {
            "Object manipulation",
            "Sonar-based object detection",
            "Tactile sensing",
            "Delicate object handling"
        };
        limitations = {
            "Relies on sonar feedback",
            "Limited to physical manipulation tasks"
        };
        
        personality = {
            "Industrious and focused on physical tasks",
            "Six grasping extensions for manipulation",
            "Sonar feedback for object detection",
            "Highly developed sense of touch",
            "Capable of delicate and precise work",
            "Primary purpose is object manipulation",
            "Can detect object characteristics through sonar"
        };
    }

    void perform_task() override;
    void report_status() override;
    void describe_personality();

private:
    std::vector<std::string> personality;
};

#endif // CWALDO_H
