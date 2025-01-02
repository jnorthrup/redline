#ifndef ROBOT_H
#define ROBOT_H

#include <string>
#include <vector>

class Robot {
protected:
    std::string name;
    int num_graspers;
    std::vector<std::string> capabilities;
    std::vector<std::string> limitations;

public:
    Robot(const std::string& name, int num_graspers)
        : name(name), num_graspers(num_graspers) {}

    virtual ~Robot() {}

    virtual void perform_task() = 0;
    virtual void report_status() = 0;

    std::string get_name() const { return name; }
    int get_num_graspers() const { return num_graspers; }
    std::vector<std::string> get_capabilities() const { return capabilities; }
    std::vector<std::string> get_limitations() const { return limitations; }
};

#endif // ROBOT_H
