#ifndef WHIZ_H
#define WHIZ_H

#include "robot.h"
#include <string>
#include <vector>
#include <memory>

class Whiz : public Robot {
public:
    Whiz() : Robot("Whiz", 4) {
        capabilities = {
            "Rapid computation",
            "Data processing",
            "Memory management",
            "Algorithm optimization",
            "Real-time analysis"
        };
        limitations = {
            "Limited to 1 meter height",
            "Requires clear memory buffers",
            "Energy-intensive computations"
        };
        
        personality = {
            "Fast and efficient",
            "Known for rapid calculations",
            "Designed by Frobozz Engineering Company",
            "Four processing extensions",
            "Specialized in data analysis",
            "Known for the phrase 'Processing complete'"
        };
    }

    void perform_task() override;
    void report_status() override;
    void describe_personality();
    
    // Specific Whiz functionality
    void process_data();
    void optimize_algorithms();
    void analyze_in_real_time();
    void clear_memory_buffers();
    bool are_memory_buffers_clear() const;
    void set_memory_buffers_clear(bool status);

private:
    std::vector<std::string> personality;
    bool memory_buffers_clear = true;
    
    // Internal methods
    void check_processing_system();
    void update_status();
};

#endif // WHIZ_H
