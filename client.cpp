#include "client.h"
#include "common/common.h"
#include "common/main_window.h"

#include <string>
#include <stdexcept>

#include <boost/throw_exception.hpp>
#include <boost/optional.hpp>

#include <QTcpSocket>

struct client_t::implementation_t
{
   QTcpSocket socket;
   main_window_t * message_handler;
   boost::optional<message_type_t> last_query_type;

   implementation_t(main_window_t * message_handler)
      : message_handler(message_handler)
   {
   }
};

client_t::client_t(main_window_t * message_handler)
   : pimpl_(new implementation_t(message_handler))
{
   connect(&pimpl_->socket, SIGNAL(connected()), SLOT(connection_established()));
   connect(&pimpl_->socket, SIGNAL(readyRead()), SLOT(start_reading()));
   connect(&pimpl_->socket, SIGNAL(error(QAbstractSocket::SocketError)),
           SLOT(handle_error(QAbstractSocket::SocketError)));
}

client_t::~client_t()
{
}

void client_t::query_list(QString const & host)
{
   if (pimpl_->socket.state() != QAbstractSocket::UnconnectedState)
   {
      qDebug() << "Already connected";
      return;
   }

   pimpl_->socket.connectToHost(host, default_port());
   pimpl_->last_query_type = MT_LIST;

   QByteArray query;
   query.push_back(static_cast<unsigned char>(MT_LIST));
   pimpl_->socket.write(query);
}

void client_t::query_get(QString const & host, std::string const & filename)
{
   if (pimpl_->socket.state() != QAbstractSocket::UnconnectedState)
   {
      qDebug() << "Already connected";
      return;
   }

   pimpl_->socket.connectToHost(host, default_port());
   pimpl_->last_query_type = MT_GET;

   QByteArray query;
   query.push_back(static_cast<unsigned char>(MT_GET));
   query.append(filename.data(), filename.size());
   query.push_back('\0');
   pimpl_->socket.write(query);
}

void client_t::query_put(QString const & host, std::string const & filename, std::string const & data)
{
   if (pimpl_->socket.state() != QAbstractSocket::UnconnectedState)
   {
      qDebug() << "Already connected";
      return;
   }

   pimpl_->socket.connectToHost(host, default_port());
   pimpl_->last_query_type = MT_PUT;

   QByteArray query;
   query.push_back(static_cast<unsigned char>(MT_PUT));
   query.append(filename.data(), filename.size());
   query.append('\0');
   std::uint64_t size = data.size();
   query.append(int_to_bytes(size));
   query.append(data.data(), data.size());
   pimpl_->socket.write(query);
}

void client_t::connection_established()
{
   qDebug() << "connection established";
}

void client_t::start_reading()
{
   QByteArray const datagram = pimpl_->socket.readAll();

   switch (*pimpl_->last_query_type)
   {
      case MT_LIST:
      {
         assert(datagram[0] == static_cast<unsigned char>(MT_LIST_RESPONSE));

         QByteArray count(datagram.data() + 1, 4);
         size_t files_count = bytes_to_int(count);
         size_t offset = 5;

         std::vector<std::pair<std::string, std::string>> files_info;
         files_info.reserve(files_count);
         for (size_t i = 0; i != files_count; ++i)
         {
            auto start = datagram.data() + offset;
            QByteArray md5(start, 16);
            std::string filename(start + 16);
            offset += (md5.size() + filename.size() + 1);
            files_info.emplace_back(human_readable_md5(md5), std::move(filename));
         }

         pimpl_->message_handler->handle_list_response(files_info);
         break;
      }
      case MT_GET:
      {
         assert(datagram[0] == static_cast<unsigned char>(MT_GET_RESPONSE));
         QByteArray size(datagram.data() + 1, 4);
         size_t file_size = bytes_to_int(size);
         auto start = datagram.data() + 5;
         QByteArray hash(start, 16);
         start += 16;
         std::string file_data(start, start + file_size);
         pimpl_->message_handler->handle_get_response(std::make_pair(human_readable_md5(hash),
                                                                     std::move(file_data)));

         break;
      }
      default:
         assert(false);
   }
}

void client_t::handle_error(QAbstractSocket::SocketError err)
{
   switch (err)
   {
      case QAbstractSocket::RemoteHostClosedError:
         break;
      case QAbstractSocket::HostNotFoundError:
         pimpl_->message_handler->handle_error("The host was not found. Please check the host name and port settings.");
         break;
      case QAbstractSocket::ConnectionRefusedError:
         pimpl_->message_handler->handle_error("The connection was refused by the peer.");
         break;
      default:
         pimpl_->message_handler->handle_error("The following error occurred: " + pimpl_->socket.errorString());
   }
}
