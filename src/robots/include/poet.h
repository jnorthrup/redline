#ifndef POET_H
#define POET_H

#include "robot.h"
#include <string>
#include <vector>
#include <memory>

class Poet : public Robot {
public:
    Poet() : Robot("Poet", 3) {
        capabilities = {
            "Metaphorical communication",
            "Pattern recognition",
            "Electrical diagnostics",
            "Flow analysis",
            "Creative problem solving"
        };
        limitations = {
            "Limited to 1 meter height",
            "Abstract thinking patterns",
            "Requires clear data streams"
        };
        
        personality = {
            "Creative and abstract",
            "Known for poetic expressions",
            "Designed by Frobozz Engineering Company",
            "Three diagnostic extensions",
            "Specialized in pattern analysis",
            "Known for the phrase 'The flow of metaphor'"
        };
    }

    void perform_task() override;
    void report_status() override;
    void describe_personality();
    
    // Specific Poet functionality
    void analyze_patterns();
    void diagnose_electrical_flow();
    void communicate_metaphorically(const std::string& message);
    void clear_data_streams();
    bool are_data_streams_clear() const;
    void set_data_streams_clear(bool status);

private:
    std::vector<std::string> personality;
    bool data_streams_clear = true;
    
    // Internal methods
    void check_diagnostic_system();
    void update_status();
};

#endif // POET_H
