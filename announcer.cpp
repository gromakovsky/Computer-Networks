#include "announcer.h"
#include "common/common.h"
#include "common/host.h"
#include "common/main_window.h"

#include <cstdint>
#include <iostream>
#include <ctime>
#include <functional>

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

   typedef std::function<void(host_t &&)> host_added_callback_t;
   host_added_callback_t host_added_callback;
   typedef std::function<void(QString const &)> error_callback_t;
   error_callback_t error_callback;

   implementation_t(QByteArray const & ip, std::string const & name, fs::path const & path,
                    host_added_callback_t const & host_added_callback,
                    error_callback_t const & error_callback)
      : ip(ip)
      , name(name)
      , path(path)
      , host_added_callback(host_added_callback)
      , error_callback(error_callback)
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
         error_callback(socket.errorString());
      }
      else if (res != msg.size())
      {
         error_callback("Datagram was not fully sent");
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
            error_callback("Received truncated UDP datagram with size " + QString::number(datagram.size()));
         }

         std::string const ip = parse_ip(datagram.data());
         std::string const name(datagram.data() + 16);
         size_t files_count = bytes_to_int(QByteArray(datagram.data() + 4, 4));
         std::uint64_t timestamp = bytes_to_int(QByteArray(datagram.data() + 8, 8));

         host_added_callback(host_t(ip, name, files_count, timestamp));
      }
   }
};

announcer_t::announcer_t(QByteArray const & ip, std::string const & name, boost::filesystem::path const & path)
   : pimpl_(new implementation_t(ip, name, path, [this](host_t && host){emit host_added(std::move(host));},
                                                 [this](QString const & e){emit error_occured(e);})
                                 )
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
