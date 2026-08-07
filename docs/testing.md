# Testing

This project uses two test suites: C++ tests for the native bridge, and Python tests for the application layer.

## Prerequisites

- **CMake** 3.16+
- **C++ compiler** with C++17 support (GCC, Clang, or MSVC)
- **Python** 3.11+
- **Git** (for FetchContent to download GoogleTest)

## Installing Test Dependencies

```bash
# Python test dependencies
python -m pip install -r requirements-dev.txt
```

## Running C++ Tests

```bash
# Configure (downloads GoogleTest on first run)
cmake -S native_bridge -B native_bridge/build

# Build tests
cmake --build native_bridge/build --target multi_earbud_bridge_tests

# Run tests
cd native_bridge/build
ctest --output-on-failure
```

## Running Python Tests

```bash
# From the project root
python -m pytest tests/ -v
```

## Running All Tests

```bash
# C++
cmake -S native_bridge -B native_bridge/build
cmake --build native_bridge/build --target multi_earbud_bridge_tests
cd native_bridge/build && ctest --output-on-failure

# Python
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Test Structure

```
native_bridge/tests/
    test_types.cpp          # C++ tests for ErrorCode enum and JSON serialization

tests/
    __init__.py             # Package marker
    test_driver_capabilities.py  # DriverCapabilities model tests
    test_bridge_errors.py        # BridgeError exception hierarchy tests
```

## Writing New Tests

### C++
- Add test files to `native_bridge/tests/`.
- Register new test files in `native_bridge/CMakeLists.txt` by appending to the `add_executable(multi_earbud_bridge_tests ...)` sources list.
- Use the `bridge::tests` namespace.

### Python
- Add test files to `tests/`.
- Use `pytest` conventions (functions named `test_*`, files named `test_*.py`).
- Import from `src.audio` or other application modules as needed.
