#pragma once

#include "common/host.h"

#include <string>
#include <memory>

#include <QObject>
#include <QByteArray>

#include <boost/filesystem/path.hpp>

struct announcer_t : public QObject
{
   Q_OBJECT

public:
   announcer_t(QByteArray const & ip, std::string const & name, boost::filesystem::path const &);
   ~announcer_t();

   void start();
   
signals:
   void host_added(host_t host);
   void error_occured(QString const & description);

private slots:
   void send_announce() const;
   void read_announce() const;

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
