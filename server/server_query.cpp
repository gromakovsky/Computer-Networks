#include "server_query.h"
#include "response_message_constructor.h"
#include "common/common.h"
#include "common/main_window.h"
#include "common/reader.h"
#include "common/writer.h"

#include <QTcpSocket>
#include <QByteArray>

#include <boost/range/algorithm/copy.hpp>
#include <boost/optional.hpp>
#include <boost/filesystem.hpp>
#include <boost/filesystem/fstream.hpp>

namespace fs = boost::filesystem;

struct server_query_t::implementation_t
{
   QTcpSocket * socket;
   fs::path const path;

   QByteArray buffer;
   reader_t reader;
   writer_t writer;

   bool finished;

   implementation_t(QTcpSocket * socket, fs::path const & path)
      : socket(socket)
      , path(path)
      , reader(socket)
      , writer(socket)
      , finished(false)
   {
   }

   void data_read(QByteArray const & data)
   {
      buffer.append(data);
      auto message_type = static_cast<message_type_t>(buffer.at(0));
      switch (message_type)
      {
         case MT_LIST:
         {
            writer.consume(construct_list_response(path));
            writer.finish();
            break;
         }
         case MT_GET:
         {
            auto it = std::find(buffer.begin(), buffer.end(), '\0');
            if (it != buffer.end())
            {
               std::string filename(std::next(buffer.begin()), it);
               writer.consume(construct_get_response(path / filename));
               writer.finish();
            }
            break;
         }
         case MT_PUT:
         {
            auto idx = std::distance(buffer.begin(), std::find(buffer.begin(), buffer.end(), '\0'));
            if (idx + 8 < buffer.size())
            {
               size_t size_start_idx = idx + 1;
               size_t size = bytes_to_int(buffer.mid(size_start_idx, 8));
               size_t data_start_idx = size_start_idx + 8;
               if (data_start_idx + size <= static_cast<size_t>(buffer.size()))
               {
                  std::string filename(std::next(buffer.data()), idx - 1);
                  fs::ofstream out(path / filename, std::ios_base::binary);
                  boost::copy(buffer.mid(data_start_idx, size), std::ostream_iterator<char>(out));
               }
            }
            break;
         }
         default:
            assert(false);
      }
   }

   QString get_error_description(QAbstractSocket::SocketError err)
   {
//      switch (err)
//      {
//         case QAbstractSocket::RemoteHostClosedError:
//            break;
//         case QAbstractSocket::HostNotFoundError:
//            main_window->handle_error("The host was not found. Please check the host name and port settings.");
//            break;
//         case QAbstractSocket::ConnectionRefusedError:
//            main_window->handle_error("The connection was refused by the peer.");
//            break;
//         default:
//            main_window->handle_error("The following error occurred: " + socket->errorString());
//      }
      return socket->errorString();
   }
};

server_query_t::server_query_t(QObject * parent, QTcpSocket * socket, fs::path const & path)
   : QObject(parent)
   , pimpl_(new implementation_t(socket, path))
{
   assert(socket->state() == QAbstractSocket::ConnectedState);
   connect(&pimpl_->reader, SIGNAL(data_read(QByteArray const &)), SLOT(data_read(QByteArray const &)));
   connect(pimpl_->socket, SIGNAL(error(QAbstractSocket::SocketError)),
           SLOT(display_error(QAbstractSocket::SocketError)));

   connect(&pimpl_->writer, SIGNAL(finished()), SLOT(finish()));
}

server_query_t::~server_query_t()
{
}

void server_query_t::data_read(QByteArray const & data)
{
   pimpl_->data_read(data);
}

void server_query_t::display_error(QAbstractSocket::SocketError err)
{
   // It's OK if client has closed connection after reading all the data
   if (pimpl_->finished && err == QAbstractSocket::RemoteHostClosedError)
      return;

   emit error_occured(pimpl_->get_error_description(err));
}

void server_query_t::finish()
{
   pimpl_->finished = true;
//   pimpl_->socket->close();
//   pimpl_->socket->deleteLater();
//   deleteLater();
}
