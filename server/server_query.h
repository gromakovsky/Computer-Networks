#pragma once

#include <memory>

#include <QObject>
#include <QAbstractSocket>

#include <boost/filesystem/path.hpp>

class QTcpSocket;
struct main_window_t;

struct server_query_t : QObject
{
   Q_OBJECT

public:
   server_query_t(QObject * parent, QTcpSocket * socket, boost::filesystem::path const &);
   ~server_query_t();

signals:
   void error_occured(QString const & description);

private slots:
   void data_read(QByteArray const &);
   void display_error(QAbstractSocket::SocketError err);

   void disconnected();
   void finish();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
