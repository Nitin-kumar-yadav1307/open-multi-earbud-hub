#pragma once

#include <memory>

#include "backend.hpp"

namespace bridge {

std::unique_ptr<AudioBackend> createBackend();

}  // namespace bridge
