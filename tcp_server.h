#pragma once

#include <memory>

#include <QObject>

#include <boost/filesystem/path.hpp>

struct message_handler_t;

struct tcp_server_t : QObject
{
   Q_OBJECT

public:
   tcp_server_t(message_handler_t * message_handler, boost::filesystem::path const & path);
   ~tcp_server_t();

private slots:
   void accept_connection();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
