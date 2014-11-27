#include "common/common.h"
#include "announcer.h"
#include "host.h"
#include "common/message_handler.h"

#include <cstdint>
#include <iostream>
#include <ctime>

#include <QUdpSocket>
#include <QTimer>

#include <boost/filesystem.hpp>
#include <boost/throw_exception.hpp>

namespace fs = boost::filesystem;

namespace
{
   std::string parse_ip(char const * ip)
   {
      std::string res;

      for (size_t i = 0; i != 4; ++i)
      {
         unsigned char c = ip[i];
         res += std::to_string(static_cast<unsigned int>(c));
         res += ".";
      }

      return res.substr(0, res.length() - 1);
   }

}

struct announcer_t::implementation_t
{
   QByteArray const ip;
   std::string const name;
   fs::path const path;

   QUdpSocket socket;
   QTimer timer;

   message_handler_t * message_handler;

   implementation_t(QByteArray const & ip, std::string const & name, fs::path const & path,
                    message_handler_t * message_handler)
      : ip(ip)
      , name(name)
      , path(path)
      , message_handler(message_handler)
   {
   }

   QByteArray compose_message() const
   {
      QByteArray res;
      res.reserve(16 + name.length());
      std::uint64_t last_modification_time = fs::last_write_time(path) * 1000;
      res.append(ip)
            .append(int_to_bytes(get_files_count(path)))
            .append(int_to_bytes(last_modification_time))
            .append(name.c_str())
            .append('\0')
            ;

      return res;
   }

   void start()
   {
      socket.bind(default_port(), QUdpSocket::ShareAddress);
      timer.start(1000);
   }

   void send_msg()
   {
      auto msg = compose_message();
      auto res = socket.writeDatagram(msg, QHostAddress::Broadcast, default_port());
      if (res == -1)
      {
         message_handler->handle_error(socket.errorString());
      }
      else if (res != msg.size())
      {
         message_handler->handle_error("Datagram was not fully sent");
      }
   }

   void read_msg()
   {
      while (socket.hasPendingDatagrams())
      {
         QByteArray datagram;
         datagram.resize(socket.pendingDatagramSize());
         socket.readDatagram(datagram.data(), datagram.size());
         if (datagram.size() <= 16)
         {
            BOOST_THROW_EXCEPTION(std::runtime_error("Received truncated datagram with size "
                                                     + std::to_string(datagram.size())));
         }

         std::string const ip = parse_ip(datagram.data());
         std::string const name(datagram.data() + 16);
         size_t files_count = bytes_to_int(QByteArray(datagram.data() + 4, 4));
         std::uint64_t timestamp = bytes_to_int(QByteArray(datagram.data() + 8, 8));

         message_handler->add_host(host_t(ip, name, files_count, timestamp));
      }
   }
};

announcer_t::announcer_t(QByteArray const & ip, std::string const & name, boost::filesystem::path const & path,
                         message_handler_t * message_handler)
   : pimpl_(new implementation_t(ip, name, path, message_handler))
{
   connect(&pimpl_->timer, SIGNAL(timeout()), SLOT(send_announce()));
   connect(&pimpl_->socket, SIGNAL(readyRead()), SLOT(read_announce()));
}

announcer_t::~announcer_t()
{
}

void announcer_t::start()
{
   pimpl_->start();
}

void announcer_t::send_announce() const
{
   pimpl_->send_msg();
}

void announcer_t::read_announce() const
{
   pimpl_->read_msg();
}
