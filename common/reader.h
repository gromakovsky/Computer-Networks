#pragma once

#include <memory>

#include <QObject>

class QTcpSocket;
class QByteArray;

struct reader_t : QObject
{
   Q_OBJECT

public:
   reader_t(QTcpSocket * socket);
   ~reader_t();

signals:
   void data_read(QByteArray const & data);

private slots:
   void read();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
