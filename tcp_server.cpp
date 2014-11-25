#include "common.h"
#include "tcp_server.h"
#include "message_handler.h"
#include "query.h"

#include <cassert>
#include <iostream>

#include <QTcpServer>
#include <QTcpSocket>

namespace fs = boost::filesystem;

struct tcp_server_t::implementation_t
{
   QTcpServer server;
   QTcpSocket socket;

   message_handler_t * message_handler;
   fs::path const path;

   implementation_t(message_handler_t * message_handler, fs::path const & path)
      : message_handler(message_handler)
      , path(path)
   {
      if (!server.listen(QHostAddress::Any, default_port()))
      {
          message_handler->handle_error("Unable to start the server: " + server.errorString());
          return;
      }
   }
};

tcp_server_t::tcp_server_t(message_handler_t * message_handler, boost::filesystem::path const & path)
   : pimpl_(new implementation_t(message_handler, path))
{
   connect(&pimpl_->server, SIGNAL(newConnection()), SLOT(accept_connection()));
}

tcp_server_t::~tcp_server_t()
{
}

void tcp_server_t::accept_connection()
{
   assert(pimpl_->server.hasPendingConnections());
   new query_t(this, pimpl_->server.nextPendingConnection(), pimpl_->message_handler, pimpl_->path);
}
