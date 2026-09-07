#pragma once

inline int objective(int candidate, int target) {
    return (candidate - target) * (candidate - target);
}
