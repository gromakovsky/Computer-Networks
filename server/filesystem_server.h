#pragma once

#include <memory>

#include <QObject>

#include <boost/filesystem/path.hpp>

struct filesystem_server_t : QObject
{
   Q_OBJECT

public:
   filesystem_server_t(boost::filesystem::path const &);
   ~filesystem_server_t();

signals:
   void error_occured(QString const & description);

private slots:
   void accept_connection();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
