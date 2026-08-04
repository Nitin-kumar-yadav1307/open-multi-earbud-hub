#pragma once

#include <string>
#include <vector>

namespace bridge {

struct ProcessResult {
    int exitCode = -1;
    std::string output;
};

std::string shellQuote(const std::string& text);
std::string buildCommand(const std::string& program, const std::vector<std::string>& args);
ProcessResult runCommandCapture(const std::string& command);
int runCommand(const std::string& command);

}  // namespace bridge
