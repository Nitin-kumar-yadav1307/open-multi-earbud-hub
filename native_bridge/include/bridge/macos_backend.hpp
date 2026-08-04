#pragma once

#include "backend.hpp"

namespace bridge {

class MacOSBackend final : public AudioBackend {
   public:
    MacOSBackend();

    std::vector<SinkInfo> listSinks() override;
    void setVolume(const std::string& sinkName, int volumePercent) override;
    void updateHub() override;
    void unloadHub() override;
    bool hasUsableHubDevice() override;

   private:
    std::string currentOutputDevice();
    bool isVirtualHubDevice(const std::string& deviceName) const;

    std::string previousOutputDevice_;
};

}  // namespace bridge
