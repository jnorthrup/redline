#ifndef SENSA_H
#define SENSA_H

#include <string>
#include <vector>
#include <iostream>

class Sensa {
public:
    Sensa();
    
    void analyze_environment();
    void report_findings();
    void set_sensitivity_level(int level);
    int get_sensitivity_level() const;
    
private:
    int sensitivity_level = 5;
    std::vector<std::string> sensor_data;
};

#endif // SENSA_H
