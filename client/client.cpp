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
   std::unique_ptr<QTcpSocket> socket(new QTcpSocket);
   socket->connectToHost(request.host, default_port());
   qDebug() << "Waiting for connected";
   socket->waitForConnected();
   qDebug() << "Connected";
   assert(socket->state() == QAbstractSocket::ConnectedState);
   auto query = new client_query_t(this, socket.release(), request);
   connect(query, SIGNAL(response_arrived(response_t const &)), SIGNAL(response_arrived(response_t const &)));
   connect(query, SIGNAL(error_occured(QString const &)), SIGNAL(error_occured(QString const &)));
}

void client_t::handle_error(QAbstractSocket::SocketError err)
{
//   switch (err)
//   {
//      case QAbstractSocket::RemoteHostClosedError:
//         break;
//      case QAbstractSocket::HostNotFoundError:
//         pimpl_->message_handler->handle_error("The host was not found. Please check the host name and port settings.");
//         break;
//      case QAbstractSocket::ConnectionRefusedError:
//         pimpl_->message_handler->handle_error("The connection was refused by the peer.");
//         break;
//      default:
//         pimpl_->message_handler->handle_error("The following error occurred: " + pimpl_->socket.errorString());
//   }
}
