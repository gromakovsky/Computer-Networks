#pragma once

#include <string>
#include <cstddef>

struct host_t
{
   std::string const ip;
   std::string const name;
   size_t const files_count;
   std::uint64_t const timestamp;

   host_t(std::string const & ip, std::string const & name, size_t files_count, std::uint64_t timestamp)
      : ip(ip)
      , name(name)
      , files_count(files_count)
      , timestamp(timestamp)
   {
   }
};
