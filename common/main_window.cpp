#include "main_window.h"

#include "announcer.h"
#include "server/filesystem_server.h"
#include "client/client.h"

#include <unordered_map>

#include <QTableWidget>
#include <QVBoxLayout>
#include <QMessageBox>
#include <QDebug>
#include <QLabel>
#include <QTextEdit>
#include <QPushButton>

#include <boost/format.hpp>

struct main_window_t::implementation_t
{
   QTableWidget table;
   QTextEdit msg_host_edit;
   QTextEdit msg_type_edit;
   QTextEdit msg_args_edit;
   QPushButton msg_send_button;
   QLabel response_label;
   std::unordered_map<std::string, size_t> entries; // name -> row

   announcer_t announcer;
   filesystem_server_t server;
   client_t client;

   implementation_t(QByteArray const & ip, std::string const & name, boost::filesystem::path const & path,
                    main_window_t * main_window)
      : table(0, 4)
      , msg_host_edit("localhost")
      , msg_type_edit("LIST")
      , msg_send_button("Send")
      , announcer(ip, name, path)
      , server(path)
      , client(main_window)
   {
      announcer.start();
      table.setHorizontalHeaderLabels(QStringList()
                                      << "IP"
                                      << "Name"
                                      << "Files count"
                                      << "Timestamp"
                                      );
   }
};

main_window_t::main_window_t(QByteArray const & ip, std::string const & name, boost::filesystem::path const & path)
   : pimpl_(new implementation_t(ip, name, path, this))
{
   QHBoxLayout * msg_send_layout = new QHBoxLayout;
   msg_send_layout->addWidget(&pimpl_->msg_host_edit);
   msg_send_layout->addWidget(&pimpl_->msg_type_edit);
   msg_send_layout->addWidget(&pimpl_->msg_args_edit);
   msg_send_layout->addWidget(&pimpl_->msg_send_button);
   QVBoxLayout * layout = new QVBoxLayout;
   layout->addLayout(msg_send_layout);
   layout->addWidget(&pimpl_->response_label);
   layout->addWidget(&pimpl_->table);
   setLayout(layout);

   connect(&pimpl_->msg_send_button, SIGNAL(clicked()), SLOT(send_query()));

   connect(&pimpl_->announcer, SIGNAL(host_added(host_t)), SLOT(add_host(host_t)));
   connect(&pimpl_->announcer, SIGNAL(error_occured(QString const &)), SLOT(handle_error(QString const &)));

   connect(&pimpl_->server, SIGNAL(error_occured(QString const &)), SLOT(handle_error(QString const &)));
}

main_window_t::~main_window_t()
{
}

void main_window_t::add_host(host_t host)
{
   auto it = pimpl_->entries.find(host.name);
   if (it == pimpl_->entries.end())
   {
      size_t idx = pimpl_->table.rowCount();

      pimpl_->table.insertRow(idx);
      pimpl_->table.setItem(idx, 0, new QTableWidgetItem(host.ip.c_str()));
      pimpl_->table.setItem(idx, 1, new QTableWidgetItem(host.name.c_str()));
      pimpl_->table.setItem(idx, 2, new QTableWidgetItem(std::to_string(host.files_count).c_str()));
      pimpl_->table.setItem(idx, 3, new QTableWidgetItem(std::to_string(host.timestamp).c_str()));

      pimpl_->entries.emplace(std::move(host.name), idx);
   }
   else
   {
      size_t idx = it->second;

      pimpl_->table.item(idx, 0)->setText(host.ip.c_str());
      pimpl_->table.item(idx, 1)->setText(host.name.c_str());
      pimpl_->table.item(idx, 2)->setText(QString::number(host.files_count));
      pimpl_->table.item(idx, 3)->setText(QString::number(host.timestamp));
   }
}

void main_window_t::handle_error(QString const & description)
{
   QMessageBox::critical(this, "Error occured", description);
}

void main_window_t::handle_list_response(std::vector<std::pair<std::string, std::string> > const & files_info)
{
   std::string msg = "Last response (to 'LIST' query):\n";
   for (auto const & pair : files_info)
   {
      msg += pair.second + " (md5 = " + pair.first + ")\n";
   }
   pimpl_->response_label.setText(msg.c_str());
}

void main_window_t::handle_get_response(std::pair<std::string, std::string> const & fileinfo)
{
   auto msg = boost::format("Last response (to 'GET' query):\nSize = %1%, md5 = %2%, data:\n%3%")
         % fileinfo.second.size()
         % fileinfo.first
         % fileinfo.second;
   pimpl_->response_label.setText(boost::str(msg).c_str());
}

void main_window_t::send_query()
{
   auto type = pimpl_->msg_type_edit.toPlainText();
   auto host = pimpl_->msg_host_edit.toPlainText();
   QString args = pimpl_->msg_args_edit.toPlainText();
   if (type == "LIST")
   {
      pimpl_->client.query_list(host);
   }
   else if (type == "GET")
   {
      pimpl_->client.query_get(host, args.toStdString());
   }
   else if (type == "PUT")
   {
      auto split = args.split("\n");
      pimpl_->client.query_put(host, split[0].toStdString(), split[1].toStdString());
   }
}
