#pragma once

#include <boost/variant/variant.hpp>

#include <QString>

struct request_t
{
   enum request_type_t
   {
      RT_LIST,
      RT_GET,
      RT_PUT,
   };

   typedef std::nullptr_t list_request_data_t;
   typedef std::string get_request_data_t;
   typedef std::pair<std::size_t, std::size_t> put_request_data_t;

   QString host;
   boost::variant<list_request_data_t, get_request_data_t, put_request_data_t> data;
};
