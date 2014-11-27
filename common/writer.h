#pragma once

#include <memory>

#include <QObject>

class QTcpSocket;
class QByteArray;

struct writer_t : QObject
{
   Q_OBJECT

public:
   writer_t(QTcpSocket * socket);
   ~writer_t();

   void start(QByteArray const & data);

signals:
   void finished();

private slots:
   void write();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
