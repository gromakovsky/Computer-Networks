#include "message_sender.h"
#include "message_handler.h"

#include <iostream>

#include <QApplication>
#include <QUdpSocket>
#include <QNetworkInterface>

namespace
{
   QByteArray my_ip()
   {
      QHostAddress addr;
      for (auto const & address : QNetworkInterface::allAddresses()) {
         if (address.protocol() == QAbstractSocket::IPv4Protocol && address != QHostAddress(QHostAddress::LocalHost))
         {
            addr = address;
            break;
         }
      }

      auto num = addr.toIPv4Address();
      QByteArray res;
      for (size_t i = 0; i != 4; ++i)
      {
         res.push_back(static_cast<char>(num >> ((3 - i) * 8)));
      }

      return res;
   }

   QByteArray my_mac()
   {
      QNetworkInterface interface;
      for (auto const & i : QNetworkInterface::allInterfaces())
      {
         if (!(i.flags() & QNetworkInterface::IsLoopBack))
         {
            interface = i;
            break;
         }
      }
      QByteArray res;
      auto parts = interface.hardwareAddress().split(":");
      for (QString const & part : parts)
      {
         res.push_back(part.toInt(nullptr, 16));
      }
      return res;
   }
}

int main(int argc, char * argv[])
{
   QApplication app(argc, argv);
   message_handler handler;
   message_sender sender(my_ip(), my_mac(), &handler);
   handler.show();
   sender.run();

   return app.exec();
}
