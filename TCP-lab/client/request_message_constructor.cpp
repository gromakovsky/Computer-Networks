#include "request_message_constructor.h"
#include "common/request.h"
#include "common/common.h"

#include <boost/variant/static_visitor.hpp>

namespace
{
   namespace fs = boost::filesystem;

   struct request_visitor_t : boost::static_visitor<QByteArray>
   {
      QByteArray operator()(request_t::list_request_data_t) const
      {
         return QByteArray();
      }

      QByteArray operator()(request_t::get_request_data_t const & data) const
      {
         return QByteArray(data.data(), data.size() + 1);
      }

      QByteArray operator()(request_t::put_request_data_t const & data) const
      {
         QByteArray result(data.first.data(), data.first.size() + 1);
         std::uint64_t size = data.second.size();
         result.append(int_to_bytes(size));
         result.append(data.second.data(), data.second.size());

         return result;
      }
   };

}

QByteArray construct_message(request_t const & request)
{
   QByteArray res;
   res.push_back(request.type);
   res.append(boost::apply_visitor(request_visitor_t(), request.data));

   return res;
}
