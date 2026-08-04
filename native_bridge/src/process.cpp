#include "bridge/process.hpp"

#include <cstdio>
#include <cstdlib>
#include <sstream>

namespace bridge {

std::string shellQuote(const std::string& text) {
#if defined(_WIN32)
    std::string quoted = "\"";
    for (char ch : text) {
        if (ch == '"' || ch == '\\') {
            quoted.push_back('\\');
        }
        quoted.push_back(ch);
    }
    quoted.push_back('"');
    return quoted;
#else
    std::string quoted = "'";
    for (char ch : text) {
        if (ch == '\'') {
            quoted += "'\"'\"'";
        } else {
            quoted.push_back(ch);
        }
    }
    quoted.push_back('\'');
    return quoted;
#endif
}

std::string buildCommand(const std::string& program, const std::vector<std::string>& args) {
    std::ostringstream command;
    command << shellQuote(program);
    for (const auto& arg : args) {
        command << ' ' << shellQuote(arg);
    }
    return command.str();
}

ProcessResult runCommandCapture(const std::string& command) {
    ProcessResult result;

#if defined(_WIN32)
    FILE* pipe = _popen(command.c_str(), "r");
#else
    FILE* pipe = popen(command.c_str(), "r");
#endif
    if (!pipe) {
        result.exitCode = -1;
        return result;
    }

    char buffer[4096];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        result.output += buffer;
    }

#if defined(_WIN32)
    result.exitCode = _pclose(pipe);
#else
    result.exitCode = pclose(pipe);
#endif
    return result;
}

int runCommand(const std::string& command) {
#if defined(_WIN32)
    return std::system(command.c_str());
#else
    return std::system(command.c_str());
#endif
}

}  // namespace bridge
