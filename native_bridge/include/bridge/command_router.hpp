#pragma once

#include "backend.hpp"
#include "command.hpp"

namespace bridge {

class CommandRouter {
   public:
    explicit CommandRouter(AudioBackend& backend);

    CommandResult run(const CommandRequest& request) const;

   private:
    AudioBackend& backend_;
};

}  // namespace bridge
