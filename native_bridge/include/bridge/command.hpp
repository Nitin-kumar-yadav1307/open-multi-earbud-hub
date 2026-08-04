#pragma once

#include <string>
#include <unordered_map>
#include <vector>

namespace bridge {

struct CommandRequest {
    std::string name;
    std::vector<std::string> args;
};

struct CommandResult {
    int exitCode = 0;
    std::string json;
};

CommandRequest parseCommandLine(int argc, char* argv[]);
std::unordered_map<std::string, CommandResult> availableCommands();

}  // namespace bridge
