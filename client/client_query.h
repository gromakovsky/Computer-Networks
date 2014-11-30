#pragma once

#include <memory>

#include <QObject>
#include <QAbstractSocket>

class QTcpSocket;

struct request_t;
struct response_t;

struct client_query_t : QObject
{
   Q_OBJECT

public:
   client_query_t(QObject * parent, QTcpSocket * socket, request_t const & request);
   ~client_query_t();

signals:
   void response_arrived(response_t const & response);
   void error_occured(QString const & description);

private slots:
   void data_read(QByteArray const &);
   void display_error(QAbstractSocket::SocketError err);

   void finish();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
