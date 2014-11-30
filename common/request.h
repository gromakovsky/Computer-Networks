#pragma once

#include "common/common.h"

#include <boost/variant/variant.hpp>

#include <QString>

struct request_t
{
   enum request_type_t
   {
      RT_LIST = MT_LIST,
      RT_GET = MT_GET,
      RT_PUT = MT_PUT,
   };

   typedef std::nullptr_t list_request_data_t;
   typedef std::string get_request_data_t;
   typedef std::pair<std::string, std::string> put_request_data_t;

   QString host;
   request_type_t type;
   boost::variant<list_request_data_t, get_request_data_t, put_request_data_t> data;
};
