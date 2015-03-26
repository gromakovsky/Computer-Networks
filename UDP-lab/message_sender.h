#pragma once

#include <string>

#include <QtCore/QObject>
#include <QtCore/QTimer>

#include <QUdpSocket>
#include <QByteArray>

struct message_handler;

class message_sender
      : QObject
{
   Q_OBJECT

public:
   message_sender(QByteArray const & my_ip, QByteArray const & my_mac, message_handler *);

   void run();

private slots:
   void send();
   void read();

private:
   QUdpSocket socket_;
   QTimer timer_;
   message_handler * handler_;

   QByteArray msg_;
};
