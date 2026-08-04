#pragma once

#include <sstream>
#include <string>

#include "types.hpp"

namespace bridge::json {

inline std::string escape(const std::string& value) {
    std::ostringstream out;
    for (char ch : value) {
        switch (ch) {
            case '\\':
                out << "\\\\";
                break;
            case '"':
                out << "\\\"";
                break;
            case '\b':
                out << "\\b";
                break;
            case '\f':
                out << "\\f";
                break;
            case '\n':
                out << "\\n";
                break;
            case '\r':
                out << "\\r";
                break;
            case '\t':
                out << "\\t";
                break;
            default:
                out << ch;
        }
    }
    return out.str();
}

inline std::string sinkList(const std::vector<SinkInfo>& sinks) {
    std::ostringstream out;
    out << "[";
    for (std::size_t index = 0; index < sinks.size(); ++index) {
        const auto& sink = sinks[index];
        if (index > 0) {
            out << ",";
        }
        out << "{"
            << "\"name\":\"" << escape(sink.name) << "\"," 
            << "\"desc\":\"" << escape(sink.description) << "\"," 
            << "\"id\":\"" << escape(sink.id) << "\""
            << "}";
    }
    out << "]";
    return out.str();
}

inline std::string reply(const BridgeReply& value) {
    std::ostringstream out;
    out << "{";
    out << "\"ok\":" << (value.ok ? "true" : "false");
    out << ",\"message\":\"" << escape(value.message) << "\"";
    out << ",\"available\":" << (value.available ? "true" : "false");
    out << ",\"sinks\":" << sinkList(value.sinks);
    out << "}";
    return out.str();
}

}  // namespace bridge::json
