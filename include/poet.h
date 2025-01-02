#ifndef POET_H
#define POET_H

#include <string>
#include <vector>
#include <iostream>

class Poet {
public:
    Poet();
    
    void compose_poem();
    void recite_poem();
    void set_inspiration(const std::string& inspiration);
    std::string get_inspiration() const;
    
private:
    std::string current_inspiration = "nature";
    std::vector<std::string> poems;
};

#endif // POET_H
