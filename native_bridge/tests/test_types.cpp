#include <gtest/gtest.h>
#include "bridge/types.hpp"
#include "bridge/json.hpp"

namespace bridge::tests {

TEST(ErrorCode, HasExpectedValues) {
    EXPECT_EQ(static_cast<int>(bridge::ErrorCode::None), 0);
    EXPECT_EQ(static_cast<int>(bridge::ErrorCode::InvalidArguments), 1);
    EXPECT_EQ(static_cast<int>(bridge::ErrorCode::BackendError), 2);
    EXPECT_EQ(static_cast<int>(bridge::ErrorCode::InternalError), 3);
}

TEST(BridgeReply, SerializesErrorCode) {
    bridge::BridgeReply reply;
    reply.ok = false;
    reply.error_code = bridge::ErrorCode::BackendError;
    reply.message = "pactl not found";

    std::string json = bridge::json::reply(reply);
    EXPECT_NE(json.find("\"error_code\":2"), std::string::npos);
    EXPECT_NE(json.find("\"message\":\"pactl not found\""), std::string::npos);
}

}  // namespace bridge::tests