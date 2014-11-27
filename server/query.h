#pragma once

#include <memory>

#include <QObject>
#include <QAbstractSocket>

#include <boost/filesystem/path.hpp>

class QTcpSocket;
struct message_handler_t;

struct query_t : QObject
{
   Q_OBJECT

public:
   query_t(QObject * parent, QTcpSocket * socket, message_handler_t * message_handler, boost::filesystem::path const &);
   ~query_t();

private slots:
   void data_read(QByteArray const &);
//   void display_error(QAbstractSocket::SocketError err);

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
