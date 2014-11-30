#include "client_query.h"
#include "request_message_constructor.h"
#include "common/common.h"
#include "common/main_window.h"
#include "common/reader.h"
#include "common/writer.h"
#include "common/response.h"

#include <functional>

#include <QTcpSocket>
#include <QByteArray>

#include <boost/range/algorithm/copy.hpp>
#include <boost/optional.hpp>


struct client_query_t::implementation_t
{
   QTcpSocket * socket;

   QByteArray buffer;
   reader_t reader;
   writer_t writer;

   typedef std::function<void(response_t const &)> response_handler_t;
   response_handler_t response_handler;

   implementation_t(QTcpSocket * socket, response_handler_t const & response_handler)
      : socket(socket)
      , reader(socket)
      , writer(socket)
      , response_handler(response_handler)
   {
   }

   void data_read(QByteArray const & data)
   {
      buffer.append(data);
      auto message_type = static_cast<message_type_t>(static_cast<unsigned char>(buffer.at(0)));
      switch (message_type)
      {
         case MT_LIST_RESPONSE:
         {
            if (buffer.size() < 5)
               return;

            QByteArray count(buffer.data() + 1, 4);
            size_t files_count = bytes_to_int(count);
            size_t offset = 5;

            std::vector<std::pair<std::string, std::string>> files_info;
            files_info.reserve(files_count);
            for (size_t i = 0; i != files_count; ++i)
            {
               if (offset + 16 > static_cast<size_t>(buffer.size()))
                  return;

               auto start = buffer.data() + offset;
               QByteArray md5(start, 16);
               offset += md5.size();
               start += md5.size();
               auto it = std::find(start, buffer.end(), '\0');
               if (it == buffer.end())
                  return;

               std::string filename(start, it);
               offset += (filename.size() + 1);
               files_info.emplace_back(human_readable_md5(md5), std::move(filename));
            }
            response_t response;
            response.type = response_t::RT_LIST;
            response.data = files_info;
            response_handler(response);
            reader.stop();
            break;
         }
         case MT_GET_RESPONSE:
         {
            if (buffer.size() < 5)
               return;

            QByteArray size(buffer.data() + 1, 4);
            size_t file_size = bytes_to_int(size);
            auto start = buffer.data() + 5;
            if (5 + 16 + file_size > static_cast<size_t>(buffer.size()))
               return;

            QByteArray hash(start, 16);
            start += 16;
            std::string file_data(start, start + file_size);
            response_t response;
            response.type = response_t::RT_GET;
            response.data = std::make_pair(human_readable_md5(hash), std::move(file_data));
            response_handler(response);
            reader.stop();
            break;
         }
         case MT_ERROR:
         {
            response_t response;
            response.type = response_t::RT_ERROR;
            response.data = static_cast<error_type>(buffer.at(1));
            response_handler(response);
            reader.stop();
            break;
         }
         default:
            assert(false);
      }
   }

   QString get_error_description(QAbstractSocket::SocketError err)
   {
      return socket->errorString();
   }
};

client_query_t::client_query_t(QObject * parent, QTcpSocket * socket, request_t const & request)
   : QObject(parent)
   , pimpl_(new implementation_t(socket, [this](response_t const & r){emit response_arrived(r);}))
{
   assert(socket->state() == QAbstractSocket::ConnectedState);
   connect(&pimpl_->reader, SIGNAL(data_read(QByteArray const &)), SLOT(data_read(QByteArray const &)));
   connect(pimpl_->socket, SIGNAL(error(QAbstractSocket::SocketError)),
           SLOT(display_error(QAbstractSocket::SocketError)));

   connect(&pimpl_->reader, SIGNAL(finished()), SLOT(finish()));

   connect(&pimpl_->writer, SIGNAL(error_occured(QString const &)), SIGNAL(error_occured(QString const &)));
   pimpl_->writer.consume(construct_message(request));
   pimpl_->writer.finish();
}

client_query_t::~client_query_t()
{
}

void client_query_t::data_read(QByteArray const & data)
{
   pimpl_->data_read(data);
}

void client_query_t::display_error(QAbstractSocket::SocketError err)
{
   emit error_occured(pimpl_->get_error_description(err));
}

void client_query_t::finish()
{
   pimpl_->socket->close();
   pimpl_->socket->deleteLater();
   emit finished();
   deleteLater();
}
