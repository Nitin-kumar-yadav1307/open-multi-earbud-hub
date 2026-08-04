#include "bridge/command_router.hpp"

#include <stdexcept>

#include "bridge/json.hpp"

namespace bridge {

namespace {

int parseVolume(const std::string& text) {
    int value = std::stoi(text);
    if (value < 0 || value > 100) {
        throw std::out_of_range("volume must be between 0 and 100");
    }
    return value;
}

std::string buildHelpMessage() {
    return "Available commands: list_sinks, set_volume, update_hub, unload_hub, has_usable_hub_device, help";
}

CommandResult makeResult(const BridgeReply& reply, int exitCode = 0) {
    return {exitCode, json::reply(reply)};
}

}  // namespace

CommandRouter::CommandRouter(AudioBackend& backend) : backend_(backend) {}

CommandResult CommandRouter::run(const CommandRequest& request) const {
    BridgeReply reply;

    if (request.name == "help") {
        reply.ok = true;
        reply.message = buildHelpMessage();
        return makeResult(reply);
    }

    if (request.name == "list_sinks") {
        reply.sinks = backend_.listSinks();
        reply.available = backend_.hasUsableHubDevice();
        return makeResult(reply);
    }

    if (request.name == "set_volume") {
        if (request.args.size() < 2) {
            throw std::invalid_argument("set_volume requires sink_name and volume_percent");
        }
        backend_.setVolume(request.args[0], parseVolume(request.args[1]));
        return makeResult(reply);
    }

    if (request.name == "update_hub") {
        backend_.updateHub();
        return makeResult(reply);
    }

    if (request.name == "unload_hub") {
        backend_.unloadHub();
        return makeResult(reply);
    }

    if (request.name == "has_usable_hub_device") {
        reply.available = backend_.hasUsableHubDevice();
        return makeResult(reply);
    }

    throw std::invalid_argument("unknown command: " + request.name);
}

}  // namespace bridge
