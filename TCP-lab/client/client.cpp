#include "client.h"
#include "client_query.h"
#include "common/request.h"
#include "common/common.h"

#include <string>
#include <stdexcept>

#include <boost/optional.hpp>

#include <QTcpSocket>

struct client_t::implementation_t
{
   size_t queries_count;

   implementation_t()
      : queries_count(0)
   {
   }
};

client_t::client_t()
   : pimpl_(new implementation_t())
{
}

client_t::~client_t()
{
}

void client_t::process_request(request_t const & request)
{
   static const size_t connections_limit = 32;
   if (pimpl_->queries_count >= connections_limit)
   {
      emit error_occured("Too many connections");
      return;
   }

   std::unique_ptr<QTcpSocket> socket(new QTcpSocket);
   socket->connectToHost(request.host, default_port());
   if (!socket->waitForConnected())
   {
      emit error_occured("Could not connect:\n" + socket->errorString());
      return;
   }
   assert(socket->state() == QAbstractSocket::ConnectedState);
   auto query = new client_query_t(this, socket.release(), request);
   ++pimpl_->queries_count;
   connect(query, SIGNAL(response_arrived(response_t const &)), SIGNAL(response_arrived(response_t const &)));
   connect(query, SIGNAL(error_occured(QString const &)), SIGNAL(error_occured(QString const &)));
   connect(query, SIGNAL(finished()), SLOT(query_finished()));
}

void client_t::query_finished()
{
   assert(pimpl_->queries_count);
   --pimpl_->queries_count;
}
