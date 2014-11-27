#include "reader.h"

#include <QByteArray>
#include <QTcpSocket>

struct reader_t::implementation_t
{
   QTcpSocket * socket;
   QByteArray data;

   implementation_t(QTcpSocket * socket)
      : socket(socket)
   {
   }

   void read()
   {
      auto size = socket->bytesAvailable();
      qDebug() << size;
      data.resize(size);
      socket->read(data.data(), size);
   }

};

reader_t::reader_t(QTcpSocket * socket)
   : pimpl_(new implementation_t(socket))
{
   connect(pimpl_->socket, SIGNAL(readyRead()), SLOT(read()));
}

reader_t::~reader_t()
{
}

void reader_t::read()
{
   pimpl_->read();
   emit data_read(pimpl_->data);
}
