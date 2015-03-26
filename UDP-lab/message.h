#pragma once

#include <string>
#include <chrono>

typedef std::chrono::time_point<std::chrono::steady_clock, std::chrono::nanoseconds> timestamp_t;

struct message_t
{
   std::string ip;
   std::string mac;
   std::string name;
};
