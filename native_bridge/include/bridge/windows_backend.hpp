#pragma once

#include <string>

#include "backend.hpp"

namespace bridge {

class WindowsBackend final : public AudioBackend {
   public:
    WindowsBackend();

    std::vector<SinkInfo> listSinks() override;
    void setVolume(const std::string& sinkName, int volumePercent) override;
    void updateHub() override;
    void unloadHub() override;
    bool hasUsableHubDevice() override;

   private:
    std::string previousDefaultDeviceId_;

    bool isEarbudDevice(const std::string& deviceName) const;
    bool isVirtualHubDevice(const std::string& deviceName) const;
};

}  // namespace bridge
