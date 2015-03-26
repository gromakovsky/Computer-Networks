#pragma once

#include "common.h"

#include <vector>
#include <string>
#include <utility>

#include <boost/variant/variant.hpp>

struct response_t
{
   enum response_type_t
   {
      RT_LIST,
      RT_GET,
      RT_ERROR,
   };

   typedef std::vector<std::pair<std::string, std::string>> list_response_data_t;
   typedef std::pair<std::string, std::string> get_response_data_t;
   typedef error_type error_response_data_t;

   response_type_t type;
   boost::variant<list_response_data_t, get_response_data_t, error_response_data_t> data;
};
