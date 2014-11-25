#include "common.h"
#include "query.h"
#include "message_handler.h"

#include <QTcpSocket>
#include <QByteArray>

#include <boost/range/algorithm/copy.hpp>
#include <boost/optional.hpp>
#include <boost/variant.hpp>
#include <boost/filesystem.hpp>
#include <boost/filesystem/fstream.hpp>

namespace fs = boost::filesystem;

namespace
{
   QByteArray compose_error_response(error_type type)
   {
      QByteArray res;
      res.push_back(static_cast<unsigned char>(MT_ERROR));
      res.push_back(static_cast<unsigned char>(type));

      return res;
   }

   QByteArray compose_list_response(fs::path const & path)
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

   QByteArray compose_get_response(fs::path const & path)
   {
      fs::ifstream in(path, std::ios_base::binary);
      std::string raw_file;
      std::copy(std::istream_iterator<char>(in), std::istream_iterator<char>(), std::back_inserter(raw_file));

      QByteArray res;
      res.push_back(static_cast<unsigned char>(MT_GET_RESPONSE));
      std::uint32_t size = raw_file.size();
      res.append(int_to_bytes(size));
      res.append(md5(raw_file));
      res.append(raw_file.data(), raw_file.size());

      return res;
   }
}

struct query_t::implementation_t
{
   QTcpSocket * socket;
   message_handler_t * message_handler;
   fs::path const path;

   boost::optional<message_type> msg_type;
   boost::variant<boost::none_t, std::string, std::pair<std::string, std::string>> msg_args;
   boost::optional<error_type> err;

   QByteArray response;

   implementation_t(QTcpSocket * socket, message_handler_t * message_handler, fs::path const & path)
      : socket(socket)
      , message_handler(message_handler)
      , path(path)
   {
   }

   void construct_response()
   {
      if (!err && !msg_type)
         err = ET_INTERNAL_ERROR;

      if (err)
      {
         response = compose_error_response(*err);
         return;
      }

      switch (*msg_type)
      {
         case MT_LIST:
         {
            response = compose_list_response(path);
            break;
         }
         case MT_GET:
         {
            response = compose_get_response(path / boost::get<std::string>(msg_args));
            break;
         }
         case MT_PUT:
         {
            auto args = boost::get<std::pair<std::string, std::string>>(msg_args);
            fs::ofstream out(path / args.first, std::ios_base::binary);
            boost::copy(args.second, std::ostream_iterator<char>(out));
            response.clear();
            break;
         }
         case MT_ERROR:
         {
            // TODO
         }
         default:
         {
         }
      }
   }
};

query_t::query_t(QObject * parent, QTcpSocket * socket, message_handler_t * message_handler, fs::path const & path)
   : QObject(parent)
   , pimpl_(new implementation_t(socket, message_handler, path))
{
   connect(pimpl_->socket, SIGNAL(readyRead()), SLOT(read_from_socket()));
   connect(pimpl_->socket, SIGNAL(error(QAbstractSocket::SocketError)),
           SLOT(display_error(QAbstractSocket::SocketError)));
}

query_t::~query_t()
{
}

void query_t::reading_finished()
{
   pimpl_->construct_response();
   connect(pimpl_->socket, SIGNAL(bytesWritten(qint64)), SLOT(write_response(qint64)));
   if (pimpl_->response.size() != 0)
   {
      pimpl_->socket->write(pimpl_->response);
   }
}

void query_t::writing_finished()
{
   pimpl_->socket->deleteLater();
   deleteLater();
}

void query_t::read_from_socket()
{
   if (!pimpl_->msg_type)
   {
      char c;
      bool success = pimpl_->socket->getChar(&c);
      if (!success)
      {
         pimpl_->err = ET_INTERNAL_ERROR;
         pimpl_->message_handler->handle_error("Could not get message type");
         reading_finished();
         return;
      }

      pimpl_->msg_type = static_cast<message_type>(c);
   }

   switch (*pimpl_->msg_type)
   {
      case MT_LIST:
      {
         qDebug() << "Received LIST";
         pimpl_->msg_args = boost::none;
         break;
      }
      case MT_GET:
      {
         qDebug() << "Received GET";
         QByteArray filename = pimpl_->socket->readAll();
         pimpl_->msg_args = std::string(filename.begin(), filename.end());
         break;
      }
      case MT_PUT:
      {
         qDebug() << "Received PUT";
         QByteArray raw = pimpl_->socket->readAll();
         std::string filename(raw.data());
         auto start = raw.data() + filename.size() + 1;
         auto size = bytes_to_int(QByteArray(start, 8));
         std::string data = std::string(start + 8, size);
         pimpl_->msg_args = std::make_pair(filename, data);
         break;
      }
      default:
         assert(0);
   }

   reading_finished();
}

void query_t::display_error(QAbstractSocket::SocketError err)
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
         pimpl_->message_handler->handle_error("The following error occurred: " + pimpl_->socket->errorString());
   }
}

void query_t::write_response(qint64 n)
{
   if (pimpl_->response.remove(0, n).size() != 0)
   {
      pimpl_->socket->write(pimpl_->response);
   }
   else
   {
      writing_finished();
   }
}
