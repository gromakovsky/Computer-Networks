#include "common/common.h"
#include "filesystem_server.h"
#include "common/main_window.h"
#include "server_query.h"

#include <cassert>
#include <iostream>

#include <QTcpServer>
#include <QTcpSocket>

namespace fs = boost::filesystem;

struct filesystem_server_t::implementation_t
{
   QTcpServer server;
   fs::path const path;

   implementation_t(fs::path const & path)
      : path(path)
   {
   }
};

filesystem_server_t::filesystem_server_t(boost::filesystem::path const & path)
   : pimpl_(new implementation_t(path))
{
   if (!pimpl_->server.listen(QHostAddress::Any, default_port()))
   {
      emit error_occured("Unable to start the server: " + pimpl_->server.errorString());
      return;
   }
   connect(&pimpl_->server, SIGNAL(newConnection()), SLOT(accept_connection()));
}

filesystem_server_t::~filesystem_server_t()
{
}

void filesystem_server_t::accept_connection()
{
   assert(pimpl_->server.hasPendingConnections());
   auto query = new server_query_t(this, pimpl_->server.nextPendingConnection(), pimpl_->path);
   connect(query, SIGNAL(error_occured(QString const &)), SIGNAL(error_occured(QString const &)));
}
