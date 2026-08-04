#pragma once

#include <memory>
#include <string>
#include <vector>

#include "types.hpp"

namespace bridge {

class AudioBackend {
   public:
    virtual ~AudioBackend() = default;

    virtual std::vector<SinkInfo> listSinks() = 0;
    virtual void setVolume(const std::string& sinkName, int volumePercent) = 0;
    virtual void updateHub() = 0;
    virtual void unloadHub() = 0;
    virtual bool hasUsableHubDevice() = 0;
};

}  // namespace bridge
