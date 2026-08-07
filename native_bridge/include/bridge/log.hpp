#pragma once

#include <mutex>
#include <string>
#include <iostream>

namespace bridge {

enum class LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARNING = 2,
    ERROR = 3,
};

class Logger {
public:
    static Logger& instance() {
        static Logger instance;
        return instance;
    }

    void setLevel(LogLevel level) { level_ = level; }
    LogLevel getLevel() const { return level_; }

    void log(LogLevel level, const std::string& message) {
        if (level < level_) {
            return;
        }
        std::lock_guard<std::mutex> lock(mutex_);
        std::cerr << "[" << levelToString(level) << "] " << message << std::endl;
    }

private:
    LogLevel level_ = LogLevel::WARNING;
    std::mutex mutex_;

    static const char* levelToString(LogLevel level) {
        switch (level) {
            case LogLevel::DEBUG:
                return "DEBUG";
            case LogLevel::INFO:
                return "INFO";
            case LogLevel::WARNING:
                return "WARNING";
            case LogLevel::ERROR:
                return "ERROR";
        }
        return "UNKNOWN";
    }
};

inline void log_debug(const std::string& message) {
    Logger::instance().log(LogLevel::DEBUG, message);
}

inline void log_info(const std::string& message) {
    Logger::instance().log(LogLevel::INFO, message);
}

inline void log_warning(const std::string& message) {
    Logger::instance().log(LogLevel::WARNING, message);
}

inline void log_error(const std::string& message) {
    Logger::instance().log(LogLevel::ERROR, message);
}

}  // namespace bridge
