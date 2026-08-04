#pragma once

#include "backend.hpp"

namespace bridge {

class LinuxBackend final : public AudioBackend {
   public:
    std::vector<SinkInfo> listSinks() override;
    void setVolume(const std::string& sinkName, int volumePercent) override;
    void updateHub() override;
    void unloadHub() override;
    bool hasUsableHubDevice() override;
};

}  // namespace bridge
