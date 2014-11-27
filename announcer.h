#pragma once

#include <string>
#include <memory>

#include <QObject>
#include <QByteArray>

#include <boost/filesystem/path.hpp>

struct main_window_t;

struct announcer_t : public QObject
{
   Q_OBJECT

public:
   announcer_t(QByteArray const & ip, std::string const & name, boost::filesystem::path const &, main_window_t *);
   ~announcer_t();

   void start();
   
private slots:
   void send_announce() const;
   void read_announce() const;

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
