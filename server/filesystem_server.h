#pragma once

#include <memory>

#include <QObject>

#include <boost/filesystem/path.hpp>

struct main_window_t;

struct filesystem_server_t : QObject
{
   Q_OBJECT

public:
   filesystem_server_t(main_window_t *, boost::filesystem::path const &);
   ~filesystem_server_t();

private slots:
   void accept_connection();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
