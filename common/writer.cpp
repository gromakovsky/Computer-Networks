#include "writer.h"

#include <QByteArray>
#include <QTcpSocket>

struct writer_t::implementation_t
{
   QTcpSocket * socket;
   QByteArray data;

   implementation_t(QTcpSocket * socket)
      : socket(socket)
   {
   }

   void start(QByteArray const & to_write)
   {
      data = to_write;
      write_chunk();
   }

   void write_chunk()
   {
      auto res = socket->write(data);
      if (res == -1)
      {
         // TODO
         qDebug() << "Write error occured :(";
         return;
      }
      data.remove(0, res);
   }
};

writer_t::writer_t(QTcpSocket * socket)
   : pimpl_(new implementation_t(socket))
{
   connect(pimpl_->socket, SIGNAL(bytesWritten(qint64)), SLOT(write));
}

writer_t::~writer_t()
{
}

void writer_t::start(QByteArray const & data)
{
   pimpl_->start(data);
}

void writer_t::write()
{
   if (pimpl_->data.size() == 0)
   {
      emit finished();
   }
   else
   {
      pimpl_->write_chunk();
   }
}
