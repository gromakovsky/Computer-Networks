#include "writer.h"

#include <QByteArray>
#include <QTcpSocket>

struct writer_t::implementation_t
{
   QTcpSocket * socket;
   QByteArray data;

   bool all_data_consumed;

   implementation_t(QTcpSocket * socket)
      : socket(socket)
      , all_data_consumed(false)
   {
   }

   void consume(QByteArray const & to_write)
   {
      data.append(to_write);
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

void writer_t::consume(QByteArray const & data)
{
   pimpl_->consume(data);
}

void writer_t::finish()
{
   pimpl_->all_data_consumed = true;
}

void writer_t::write()
{
   if (pimpl_->data.size() == 0)
   {
      if (pimpl_->all_data_consumed)
      {
         emit finished();
      }
   }
   else
   {
      pimpl_->write_chunk();
   }
}
