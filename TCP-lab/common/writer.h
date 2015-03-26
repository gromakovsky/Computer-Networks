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

   void consume(QByteArray const & data);
   void finish();

signals:
   void finished();
   void error_occured(QString const & description);

private slots:
   void write_again(qint64);

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
