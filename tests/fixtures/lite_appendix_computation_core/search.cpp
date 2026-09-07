#include "search.hpp"
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc != 3 && argc != 4) return 2;
    const int target = std::stoi(argv[1]);
    const int steps = std::stoi(argv[2]);
    int best = 0;
    if (argc == 4) {
        best = std::stoi(argv[3]);
        if (best < 0 || best >= steps) return 3;
    } else {
        for (int candidate = 1; candidate < steps; ++candidate) {
            if (objective(candidate, target) < objective(best, target)) best = candidate;
        }
    }
    std::cout << best << " " << objective(best, target) << "\n";
}
