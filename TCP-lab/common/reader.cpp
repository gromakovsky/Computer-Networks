#include "reader.h"

#include <QByteArray>
#include <QTcpSocket>

struct reader_t::implementation_t
{
   QTcpSocket * socket;
   QByteArray data;
   bool stopped;

   typedef std::function<void(QString const &)> error_callback_t;
   error_callback_t error_callback;

   implementation_t(QTcpSocket * socket)
      : socket(socket)
      , stopped(false)
   {
   }

   void read()
   {
      if (stopped)
         return;

      auto size = socket->bytesAvailable();
      data.resize(size);
      auto res = socket->read(data.data(), size);
      if (res == -1)
      {
         error_callback(socket->errorString());
      }
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

void reader_t::stop()
{
   pimpl_->stopped = true;
   emit finished();
}

void reader_t::read()
{
   pimpl_->read();
   emit data_read(pimpl_->data);
}
