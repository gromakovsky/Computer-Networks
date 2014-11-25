#include "announcer.h"
#include "tcp_server.h"
#include "client.h"
#include "message_handler.h"

#include <iostream>

#include <boost/filesystem.hpp>

#include <QByteArray>
#include <QApplication>
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

   namespace fs = boost::filesystem;

   std::string const my_name = "Ivan Gromakovsky";
   fs::path const path = "dir";
}

int main(int argc, char * argv[])
{
   QApplication qapp(argc, argv);
   fs::create_directory(path);

   message_handler_t msg_handler;
   msg_handler.show();

   announcer_t announcer(my_ip(), my_name, path, &msg_handler);
   announcer.start();

   tcp_server_t server(&msg_handler, path);

   client_t client(&msg_handler);
   msg_handler.set_client(&client);

   return qapp.exec();
}
