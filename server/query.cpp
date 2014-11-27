#include "common/common.h"
#include "query.h"
#include "message_constructor.h"
#include "common/message_handler.h"
#include "common/reader.h"
#include "common/writer.h"

#include <QTcpSocket>
#include <QByteArray>

#include <boost/range/algorithm/copy.hpp>
#include <boost/optional.hpp>
#include <boost/filesystem.hpp>
#include <boost/filesystem/fstream.hpp>

namespace fs = boost::filesystem;

struct query_t::implementation_t
{
   QTcpSocket * socket;
   message_handler_t * message_handler;
   fs::path const path;

   QByteArray buffer;
   reader_t reader;
   writer_t writer;

   implementation_t(QTcpSocket * socket, message_handler_t * message_handler, fs::path const & path)
      : socket(socket)
      , message_handler(message_handler)
      , path(path)
      , reader(socket)
      , writer(socket)
   {
      assert(socket->state() == QAbstractSocket::ConnectedState);
   }

   void data_read(QByteArray const & data)
   {
      buffer.append(data);
      auto message_type = static_cast<message_type_t>(buffer.at(0));
      switch (message_type)
      {
         case MT_LIST:
         {
            qDebug() << "Received LIST";
            writer.consume(construct_list_response(path));
            writer.finish();
            break;
         }
         case MT_GET:
         {
            auto it = std::find(buffer.begin(), buffer.end(), '\0');
            if (it != buffer.end())
            {
               qDebug() << "Received GET";
               std::string filename(std::next(buffer.begin()), it);
               writer.consume(construct_get_response(filename));
               writer.finish();
            }
            break;
         }
         case MT_PUT:
         {
            qDebug() << "Received PUT";
            auto idx = std::distance(std::find(buffer.begin(), buffer.end(), '\0'), buffer.begin());
            if (idx + 8 < buffer.size())
            {
               size_t size = bytes_to_int(buffer.mid(idx + 1, 8));
               if (idx + 8 + size < buffer.size())
               {
                  std::string filename(std::next(buffer.data(), idx));
               }
            }
            //            QByteArray raw = pimpl_->socket->readAll();
            //            std::string filename(raw.data());
            //            auto start = raw.data() + filename.size() + 1;
            //            auto size = bytes_to_int(QByteArray(start, 8));
            //            std::string data = std::string(start + 8, size);
            //            pimpl_->msg_args = std::make_pair(filename, data);
            break;
         }
         default:
            assert(false);
      }
   }

   void display_error(QAbstractSocket::SocketError err)
   {
      switch (err)
      {
         case QAbstractSocket::RemoteHostClosedError:
            break;
         case QAbstractSocket::HostNotFoundError:
            message_handler->handle_error("The host was not found. Please check the host name and port settings.");
            break;
         case QAbstractSocket::ConnectionRefusedError:
            message_handler->handle_error("The connection was refused by the peer.");
            break;
         default:
            message_handler->handle_error("The following error occurred: " + socket->errorString());
      }
   }

//   void construct_response()
//   {
//      if (!err && !msg_type)
//         err = ET_INTERNAL_ERROR;

//      if (err)
//      {
//         response = compose_error_response(*err);
//         return;
//      }

//      switch (*msg_type)
//      {
//         case MT_LIST:
//         {
//            response = compose_list_response(path);
//            break;
//         }
//         case MT_GET:
//         {
//            response = compose_get_response(path / boost::get<std::string>(msg_args));
//            break;
//         }
//         case MT_PUT:
//         {
//            auto args = boost::get<std::pair<std::string, std::string>>(msg_args);
//            fs::ofstream out(path / args.first, std::ios_base::binary);
//            boost::copy(args.second, std::ostream_iterator<char>(out));
//            response.clear();
//            break;
//         }
//         case MT_ERROR:
//         {
//            // TODO
//         }
//         default:
//         {
//         }
//      }
//   }
};

query_t::query_t(QObject * parent, QTcpSocket * socket, message_handler_t * message_handler, fs::path const & path)
   : QObject(parent)
   , pimpl_(new implementation_t(socket, message_handler, path))
{
   connect(&pimpl_->reader, SIGNAL(data_read(QByteArray const &)), SLOT(data_read(QByteArray const &)));
//   connect(pimpl_->socket, SIGNAL(error(QAbstractSocket::SocketError)),
//           SLOT(display_error(QAbstractSocket::SocketError)));

   connect(&pimpl_->writer, SIGNAL(finished()), SLOT(deleteLater()));
}

query_t::~query_t()
{
}

void query_t::data_read(QByteArray const & data)
{
   pimpl_->data_read(data);
}

//void query_t::display_error(QAbstractSocket::SocketError err)
//{
//   pimpl_->display_error(err);
//}
