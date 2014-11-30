#include "response_message_constructor.h"
#include "common/common.h"

#include <algorithm>

#include <boost/filesystem/fstream.hpp>
#include <boost/filesystem/operations.hpp>

namespace fs = boost::filesystem;

QByteArray construct_list_response(fs::path const & path)
{
   QByteArray res;
   res.push_back(static_cast<unsigned char>(MT_LIST_RESPONSE));
   auto count = get_files_count(path);
   res.append(int_to_bytes(count));

   for (fs::directory_iterator it(path); it != fs::directory_iterator(); ++it)
   {
      fs::ifstream in(it->path(), std::ios_base::binary);
      std::string raw_file;
      std::copy(std::istream_iterator<char>(in), std::istream_iterator<char>(), std::back_inserter(raw_file));
      auto hash = md5(raw_file);
      res.append(hash);
      auto filename = it->path().filename().string();
      res.append(filename.data(), filename.size());
      res.append('\0');
   }

   return res;
}


QByteArray construct_get_response(fs::path const & path)
{
   if (!fs::exists(path))
      return construct_error_response(ET_FILE_NOT_FOUND);

   fs::ifstream in(path, std::ios_base::binary);
   if (!in)
      return construct_error_response(ET_INTERNAL_ERROR);

   std::string raw_file;
   std::copy(std::istream_iterator<char>(in), std::istream_iterator<char>(), std::back_inserter(raw_file));

   QByteArray res;
   res.push_back(static_cast<unsigned char>(MT_GET_RESPONSE));
   std::uint32_t size = raw_file.size();
   res.append(int_to_bytes(size));
   res.append(md5(raw_file));
   res.append(raw_file.data(), size);

   return res;
}


QByteArray construct_error_response(error_type type)
{
   QByteArray res;
   res.push_back(static_cast<unsigned char>(MT_ERROR));
   res.push_back(static_cast<unsigned char>(type));

   return res;
}
