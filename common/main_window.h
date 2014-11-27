#pragma once

#include "host.h"

#include <memory>

#include <QWidget>

struct client_t;

struct message_handler_t : QWidget
{
   Q_OBJECT
public:
   message_handler_t(QWidget * parent = nullptr);
   ~message_handler_t();

   void add_host(host_t const &);
   void set_client(client_t *);

   void handle_error(QString const & description);

   void handle_list_response(std::vector<std::pair<std::string, std::string>> const & files_info);
   void handle_get_response(std::pair<std::string, std::string> const & fileinfo);

private slots:
   void send_query();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
