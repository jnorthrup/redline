#ifndef AUDA_H
#define AUDA_H

#include "robot.h"
#include <string>
#include <vector>
#include <memory>

class Auda : public Robot {
public:
    Auda() : Robot("Auda", 1) {
        capabilities = {
            "Audio communication",
            "Listening and speaking",
            "Background noise filtering",
            "Verbal interface",
            "Message transmission"
        };
        limitations = {
            "Limited to 1 meter height",
            "Requires clear audio channels",
            "Vulnerable to earwax buildup"
        };
        
        personality = {
            "Verbal and communicative",
            "Known for clear audio transmission",
            "Designed by Frobozz Engineering Company",
            "Single extension with dish antennae",
            "Specialized in human-robot communication",
            "Known for the phrase 'I hear you loud and clear'"
        };
    }

    void perform_task() override;
    void report_status() override;
    void describe_personality();
    
    // Specific Auda functionality
    void listen();
    void speak(const std::string& message);
    void filter_background_noise();
    void clear_audio_channels();
    bool is_audio_clear() const;
    void set_audio_clear(bool status);

private:
    std::vector<std::string> personality;
    bool audio_clear = true;
    
    // Internal methods
    void check_audio_system();
    void update_status();
};

#endif // AUDA_H
