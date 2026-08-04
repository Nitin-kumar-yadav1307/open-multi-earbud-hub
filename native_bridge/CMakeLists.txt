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

target_include_directories(multi_earbud_bridge PRIVATE include)

if (WIN32)
    target_link_libraries(multi_earbud_bridge PRIVATE Ole32 Mmdevapi Uuid Propsys)
endif()
