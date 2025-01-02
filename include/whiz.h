#ifndef WHIZ_H
#define WHIZ_H

#include <string>
#include <vector>
#include <iostream>

class Whiz {
public:
    Whiz();
    
    void perform_calculation();
    void solve_problem();
    void set_complexity(int level);
    int get_complexity() const;
    
private:
    int complexity_level = 1;
    std::vector<std::string> calculations;
};

#endif // WHIZ_H
