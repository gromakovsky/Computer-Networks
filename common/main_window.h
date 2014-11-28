#pragma once

#include "host.h"

#include <memory>
#include <string>

#include <QWidget>

#include <boost/filesystem/path.hpp>

class QByteArray;

struct main_window_t : QWidget
{
   Q_OBJECT
public:
   main_window_t(QByteArray const & ip, std::string const & name, boost::filesystem::path const &);
   ~main_window_t();

   void handle_list_response(std::vector<std::pair<std::string, std::string>> const & files_info);
   void handle_get_response(std::pair<std::string, std::string> const & fileinfo);

private slots:
   void send_query();
   void handle_error(QString const & description);
   void add_host(host_t);

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
