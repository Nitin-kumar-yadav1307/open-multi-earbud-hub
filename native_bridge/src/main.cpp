#include <iostream>
#include <stdexcept>
#include <system_error>

#include "bridge/backend_factory.hpp"
#include "bridge/command.hpp"
#include "bridge/command_router.hpp"
#include "bridge/json.hpp"

namespace {

void printUsage() {
    std::cerr << "Usage: multi_earbud_bridge <list_sinks|set_volume|update_hub|unload_hub|has_usable_hub_device|help> [args...]\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        auto backend = bridge::createBackend();
        auto request = bridge::parseCommandLine(argc, argv);
        bridge::CommandRouter router(*backend);
        auto result = router.run(request);
        std::cout << result.json << std::endl;
        return result.exitCode;
    } catch (const std::invalid_argument& ex) {
        printUsage();
        bridge::BridgeReply reply;
        reply.ok = false;
        reply.error_code = bridge::ErrorCode::InvalidArguments;
        reply.message = ex.what();
        std::cout << bridge::json::reply(reply) << std::endl;
        return 1;
    } catch (const std::out_of_range& ex) {
        bridge::BridgeReply reply;
        reply.ok = false;
        reply.error_code = bridge::ErrorCode::InvalidArguments;
        reply.message = ex.what();
        std::cout << bridge::json::reply(reply) << std::endl;
        return 1;
    } catch (const std::system_error& ex) {
        bridge::BridgeReply reply;
        reply.ok = false;
        reply.error_code = bridge::ErrorCode::BackendError;
        reply.message = ex.what();
        std::cout << bridge::json::reply(reply) << std::endl;
        return 1;
    } catch (const std::exception& ex) {
        bridge::BridgeReply reply;
        reply.ok = false;
        reply.error_code = bridge::ErrorCode::InternalError;
        reply.message = ex.what();
        std::cout << bridge::json::reply(reply) << std::endl;
        return 1;
    }
}
