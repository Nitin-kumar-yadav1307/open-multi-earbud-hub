#include "bridge/command.hpp"

#include <stdexcept>

namespace bridge {

CommandRequest parseCommandLine(int argc, char* argv[]) {
    if (argc < 2) {
        throw std::invalid_argument("missing command");
    }

    CommandRequest request;
    request.name = argv[1];
    for (int index = 2; index < argc; ++index) {
        request.args.emplace_back(argv[index]);
    }
    return request;
}

std::unordered_map<std::string, CommandResult> availableCommands() {
    return {
        {"help", {0, ""}},
        {"list_sinks", {0, ""}},
        {"set_volume", {0, ""}},
        {"update_hub", {0, ""}},
        {"unload_hub", {0, ""}},
        {"has_usable_hub_device", {0, ""}},
    };
}

}  // namespace bridge
