cmake_minimum_required(VERSION 3.16)

project(multi_earbud_bridge LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/../native)

add_executable(multi_earbud_bridge
    src/main.cpp
    src/command.cpp
    src/command_router.cpp
    src/backend_factory.cpp
    src/process.cpp
    src/linux_backend.cpp
    src/macos_backend.cpp
    src/windows_backend.cpp
)

# Place the binary directly in native/ for single-config (Make/Ninja) and
# multi-config (Visual Studio) generators alike, so the Python wrapper and CI
# can rely on a stable path regardless of -DCMAKE_BUILD_TYPE / --config. Setting
# the per-config target property prevents the Visual Studio generator from
# appending a Release/Debug subdirectory.
set(_native_output_dir ${CMAKE_SOURCE_DIR}/../native)
set_target_properties(multi_earbud_bridge PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${_native_output_dir}
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${_native_output_dir}
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${_native_output_dir}
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO ${_native_output_dir}
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL ${_native_output_dir}
)

target_include_directories(multi_earbud_bridge PRIVATE include)

if (WIN32)
    target_link_libraries(multi_earbud_bridge PRIVATE Ole32 Mmdevapi Uuid Propsys)
endif()
