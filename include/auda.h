#ifndef AUDA_H
#define AUDA_H

#include <string>
#include <vector>
#include <iostream>

class Auda {
public:
    Auda();
    
    void listen();
    void process_audio();
    void report_audio_quality();
    void set_volume(int level);
    int get_volume() const;
    
private:
    int volume_level = 50;
    std::vector<std::string> audio_data;
};

#endif // AUDA_H
