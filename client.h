#pragma once

#include "common/common.h"

#include <memory>

#include <QObject>
#include <QAbstractSocket>

struct message_handler_t;

struct client_t : QObject
{
   Q_OBJECT

public:
   client_t(message_handler_t * message_handler);
   ~client_t();

   void query_list(QString const & host);
   void query_get(QString const & host, std::string const & filename);
   void query_put(QString const & host, std::string const & filename, std::string const & data);

private slots:
   void connection_established();
   void start_reading();
   void handle_error(QAbstractSocket::SocketError);

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
