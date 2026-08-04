#pragma once

#include <string>
#include <vector>

namespace bridge {

struct SinkInfo {
    std::string name;
    std::string description;
    std::string id;
};

struct BridgeReply {
    bool ok = true;
    std::string message;
    std::vector<SinkInfo> sinks;
    bool available = false;
};

}  // namespace bridge
