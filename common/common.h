#pragma once

#include "md5.h"

#include <cstdint>
#include <iterator>

#include <QByteArray>
#include <QString>

#include <boost/filesystem.hpp>

inline unsigned default_port()
{
   return 7777;
}

enum message_type_t
{
   MT_LIST = 0x1,
   MT_GET = 0x2,
   MT_PUT = 0x3,

   MT_LIST_RESPONSE = 0x4,
   MT_GET_RESPONSE = 0x5,

   MT_ERROR = 0xFF,
};

enum error_type
{
   ET_FILE_NOT_FOUND = 0x1,
   ET_TOO_MANY_CONNECTIONS = 0x2,
   ET_MALFORMED_MESSAGE = 0x3,

   ET_INTERNAL_ERROR = 0xFF,
};

inline std::uint32_t get_files_count(boost::filesystem::path const & path)
{
   return std::distance(boost::filesystem::directory_iterator(path), boost::filesystem::directory_iterator());
}

template <class Int>
QByteArray int_to_bytes(Int n)
{
   QByteArray res;
   res.reserve(sizeof(Int));
   for (size_t i = 0; i != sizeof(Int); ++i)
   {
      res.push_front(static_cast<char>((n >> (i * 8)) & 0xff));
   }

   return res;
}

inline std::uint64_t bytes_to_int(QByteArray const & bytes)
{
   std::uint64_t res = 0;
   for (int i = 0; i != bytes.size(); ++i)
   {
      res += bytes[bytes.size() - i - 1] << (i * 8);
   }

   return res;
}

inline QByteArray md5(std::string const & str)
{
   auto res = MD5(str).raw_bytes();
   return QByteArray(res.data(), res.size());
}

// return hex representation of digest as string
inline std::string human_readable_md5(QByteArray const & raw_md5)
{
   assert(raw_md5.size() == 16);
   std::string res;
   for (unsigned char const c : raw_md5)
   {
      auto tmp = QString::number(static_cast<unsigned int>(c), 16);
      if (c < 0x10)
      {
         tmp = "0" + tmp;
      }
      res += tmp.toStdString();
   }
   assert(res.size() == 32);

   return res;
}

