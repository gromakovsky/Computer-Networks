#pragma once

#include "host.h"
#include "response.h"

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

private slots:
   void send_query();
   void add_host(host_t);

   void handle_response(response_t const & response);
   void handle_error(QString const & description);

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
