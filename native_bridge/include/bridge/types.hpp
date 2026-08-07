#pragma once

#include <string>
#include <vector>

namespace bridge {

// Extend this enum when adding new failure modes. Corresponding Python
// exceptions should be added to ERROR_CODE_MAP in native_bridge.py.
enum class ErrorCode : int {
    None = 0,
    InvalidArguments = 1,
    BackendError = 2,
    InternalError = 3,
};

struct SinkInfo {
    std::string name;
    std::string description;
    std::string id;
};

struct BridgeReply {
    bool ok = true;
    ErrorCode error_code = ErrorCode::None;
    std::string message;
    std::vector<SinkInfo> sinks;
    bool available = false;
};

}  // namespace bridge
