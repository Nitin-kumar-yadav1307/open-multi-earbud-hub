#include "bridge/linux_backend.hpp"

#include <algorithm>
#include <cctype>
#include <iterator>
#include <regex>
#include <sstream>

#include "bridge/process.hpp"

namespace bridge {

namespace {

constexpr const char* kHubName = "MultiEarbudSink";

std::vector<std::string> splitLines(const std::string& text) {
    std::vector<std::string> lines;
    std::istringstream stream(text);
    std::string line;
    while (std::getline(stream, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        lines.push_back(line);
    }
    return lines;
}

bool containsCaseInsensitive(const std::string& value, const std::string& needle) {
    auto lower = [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); };
    std::string lhs;
    std::string rhs;
    lhs.reserve(value.size());
    rhs.reserve(needle.size());
    std::transform(value.begin(), value.end(), std::back_inserter(lhs), lower);
    std::transform(needle.begin(), needle.end(), std::back_inserter(rhs), lower);
    return lhs.find(rhs) != std::string::npos;
}

}  // namespace

std::vector<SinkInfo> LinuxBackend::listSinks() {
    auto output = runCommandCapture(buildCommand("pactl", {"list", "sinks"}));
    std::vector<SinkInfo> sinks;
    if (output.exitCode != 0) {
        return sinks;
    }

    std::regex namePattern(R"(Name:\s+(.+))");
    std::regex descPattern(R"(Description:\s+(.+))");
    auto blocks = splitLines(output.output);
    SinkInfo current;
    bool hasName = false;

    for (const auto& line : blocks) {
        std::smatch match;
        if (std::regex_search(line, match, namePattern)) {
            current.name = match[1].str();
            hasName = true;
        } else if (std::regex_search(line, match, descPattern)) {
            current.description = match[1].str();
            current.id = current.name;
            if (hasName && containsCaseInsensitive(current.name, "bluez_output")) {
                sinks.push_back(current);
            }
            current = SinkInfo{};
            hasName = false;
        }
    }

    return sinks;
}

void LinuxBackend::setVolume(const std::string& sinkName, int volumePercent) {
    auto command = buildCommand("pactl", {"set-sink-volume", sinkName, std::to_string(volumePercent) + "%"});
    runCommand(command);
}

void LinuxBackend::unloadHub() {
    auto output = runCommandCapture(buildCommand("pactl", {"list", "modules", "short"}));
    if (output.exitCode != 0) {
        return;
    }

    for (const auto& line : splitLines(output.output)) {
        if (line.find("module-combine-sink") != std::string::npos && line.find(kHubName) != std::string::npos) {
            std::istringstream stream(line);
            std::string moduleId;
            stream >> moduleId;
            if (!moduleId.empty()) {
                runCommand(buildCommand("pactl", {"unload-module", moduleId}));
            }
        }
    }
}

void LinuxBackend::updateHub() {
    auto sinks = listSinks();
    unloadHub();

    if (sinks.size() < 2) {
        return;
    }

    std::ostringstream sinkList;
    for (std::size_t index = 0; index < sinks.size(); ++index) {
        if (index > 0) {
            sinkList << ',';
        }
        sinkList << sinks[index].name;
    }

    auto command = buildCommand(
        "pactl",
        std::vector<std::string>{"load-module", "module-combine-sink", "sink_name=" + std::string(kHubName),
                                 "sink_properties=device.description=Multi-Earbud-Hub", "sinks=" + sinkList.str()}
    );

    auto result = runCommandCapture(command);
    if (result.exitCode == 0) {
        runCommand(buildCommand("pactl", std::vector<std::string>{"set-default-sink", kHubName}));
    }
}

bool LinuxBackend::hasUsableHubDevice() {
    auto sinks = listSinks();
    return std::any_of(sinks.begin(), sinks.end(), [](const SinkInfo& sink) {
        return sink.name == kHubName || containsCaseInsensitive(sink.description, "Multi-Earbud-Hub");
    });
}

}  // namespace bridge
