#include "bridge/backend_factory.hpp"

#include "bridge/linux_backend.hpp"
#include "bridge/macos_backend.hpp"
#include "bridge/windows_backend.hpp"

namespace bridge {

std::unique_ptr<AudioBackend> createBackend() {
#if defined(_WIN32)
    return std::make_unique<WindowsBackend>();
#elif defined(__APPLE__)
    return std::make_unique<MacOSBackend>();
#else
    return std::make_unique<LinuxBackend>();
#endif
}

}  // namespace bridge
