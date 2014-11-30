#include "writer.h"

#include <functional>

#include <QByteArray>
#include <QTcpSocket>

struct writer_t::implementation_t
{
   QTcpSocket * socket;
   QByteArray data;

   bool all_data_consumed;

   typedef std::function<void(QString const &)> error_callback_t;
   error_callback_t error_callback;

   implementation_t(QTcpSocket * socket, error_callback_t const & error_callback)
      : socket(socket)
      , all_data_consumed(false)
      , error_callback(error_callback)
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
         error_callback(socket->errorString());
         return;
      }
      data.remove(0, res);
   }
};

writer_t::writer_t(QTcpSocket * socket)
   : pimpl_(new implementation_t(socket, [this](QString const & e){emit error_occured(e);}))
{
   connect(pimpl_->socket, SIGNAL(bytesWritten(qint64)), SLOT(write()));
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
