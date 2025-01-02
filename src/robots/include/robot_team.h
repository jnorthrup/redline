#ifndef ROBOT_TEAM_H
#define ROBOT_TEAM_H

#include "iris.h"
#include "waldo.h"
#include "sensa.h"
#include "poet.h"
#include "whiz.h"
#include <vector>
#include <memory>

class RobotTeam {
private:
    std::vector<std::shared_ptr<Robot>> robots;

public:
    RobotTeam() {
        robots.push_back(std::make_shared<Iris>());
        robots.push_back(std::make_shared<Waldo>());
        robots.push_back(std::make_shared<Sensa>());
        robots.push_back(std::make_shared<Poet>());
        robots.push_back(std::make_shared<Whiz>());
    }

    void perform_team_tasks() {
        for (auto& robot : robots) {
            robot->perform_task();
        }
    }

    void report_team_status() {
        for (auto& robot : robots) {
            robot->report_status();
        }
    }

    std::shared_ptr<Iris> get_iris() {
        return std::dynamic_pointer_cast<Iris>(robots[0]);
    }

    std::shared_ptr<Waldo> get_waldo() {
        return std::dynamic_pointer_cast<Waldo>(robots[1]);
    }

    std::shared_ptr<Sensa> get_sensa() {
        return std::dynamic_pointer_cast<Sensa>(robots[2]);
    }

    std::shared_ptr<Poet> get_poet() {
        return std::dynamic_pointer_cast<Poet>(robots[3]);
    }

    std::shared_ptr<Whiz> get_whiz() {
        return std::dynamic_pointer_cast<Whiz>(robots[4]);
    }
};

#endif // ROBOT_TEAM_H
