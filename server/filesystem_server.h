#pragma once

#include <memory>

#include <QObject>

#include <boost/filesystem/path.hpp>

struct message_handler_t;

struct filesystem_server_t : QObject
{
   Q_OBJECT

public:
   filesystem_server_t(message_handler_t * message_handler, boost::filesystem::path const & path);
   ~filesystem_server_t();

private slots:
   void accept_connection();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
