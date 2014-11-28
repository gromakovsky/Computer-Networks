#pragma once

#include <memory>

#include <QObject>
#include <QAbstractSocket>

#include <boost/filesystem/path.hpp>

class QTcpSocket;
struct main_window_t;

struct query_t : QObject
{
   Q_OBJECT

public:
   query_t(QObject * parent, QTcpSocket * socket, boost::filesystem::path const &);
   ~query_t();

signals:
   void error_occured(QString const & description);

private slots:
   void data_read(QByteArray const &);
   void display_error(QAbstractSocket::SocketError err);

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
