#include "bridge/macos_backend.hpp"

#include <algorithm>
#include <cctype>
#include <sstream>

#include "bridge/process.hpp"

namespace bridge {

namespace {

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
    std::string lhs = value;
    std::string rhs = needle;
    std::transform(lhs.begin(), lhs.end(), lhs.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    std::transform(rhs.begin(), rhs.end(), rhs.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    return lhs.find(rhs) != std::string::npos;
}

}  // namespace

MacOSBackend::MacOSBackend() = default;

bool MacOSBackend::isVirtualHubDevice(const std::string& deviceName) const {
    return containsCaseInsensitive(deviceName, "multi-output") ||
           containsCaseInsensitive(deviceName, "aggregate") ||
           containsCaseInsensitive(deviceName, "virtual") ||
           containsCaseInsensitive(deviceName, "loopback") ||
           containsCaseInsensitive(deviceName, "blackhole") ||
           containsCaseInsensitive(deviceName, "soundflower");
}

std::vector<SinkInfo> MacOSBackend::listSinks() {
    auto result = runCommandCapture(buildCommand("SwitchAudioSource", {"-a", "-t", "output"}));
    std::vector<SinkInfo> sinks;
    if (result.exitCode != 0) {
        return sinks;
    }

    for (const auto& line : splitLines(result.output)) {
        if (containsCaseInsensitive(line, "bluetooth") || containsCaseInsensitive(line, "airpods") ||
            containsCaseInsensitive(line, "headphone") || containsCaseInsensitive(line, "earbud") ||
            containsCaseInsensitive(line, "buds")) {
            sinks.push_back({line, line, line});
        }
    }
    return sinks;
}

void MacOSBackend::setVolume(const std::string& sinkName, int volumePercent) {
    runCommand(buildCommand("SwitchAudioSource", {"-s", sinkName, "-t", "output"}));
    runCommand(buildCommand("osascript", {"-e", "set volume output volume " + std::to_string(volumePercent)}));
}

std::string MacOSBackend::currentOutputDevice() {
    auto result = runCommandCapture(buildCommand("SwitchAudioSource", {"-c", "-t", "output"}));
    if (result.exitCode != 0) {
        return {};
    }
    auto lines = splitLines(result.output);
    return lines.empty() ? std::string{} : lines.front();
}

void MacOSBackend::updateHub() {
    auto outputs = runCommandCapture(buildCommand("SwitchAudioSource", {"-a", "-t", "output"}));
    if (outputs.exitCode != 0) {
        return;
    }

    std::string virtualDevice;
    for (const auto& line : splitLines(outputs.output)) {
        if (isVirtualHubDevice(line)) {
            virtualDevice = line;
            break;
        }
    }

    if (virtualDevice.empty()) {
        return;
    }

    previousOutputDevice_ = currentOutputDevice();
    runCommand(buildCommand("SwitchAudioSource", {"-s", virtualDevice, "-t", "output"}));
}

void MacOSBackend::unloadHub() {
    if (!previousOutputDevice_.empty()) {
        runCommand(buildCommand("SwitchAudioSource", {"-s", previousOutputDevice_, "-t", "output"}));
    }
}

bool MacOSBackend::hasUsableHubDevice() {
    auto outputs = runCommandCapture(buildCommand("SwitchAudioSource", {"-a", "-t", "output"}));
    if (outputs.exitCode != 0) {
        return false;
    }

    for (const auto& line : splitLines(outputs.output)) {
        if (isVirtualHubDevice(line)) {
            return true;
        }
    }
    return false;
}

}  // namespace bridge
