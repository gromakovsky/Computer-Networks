#include "announcer.h"
#include "server/filesystem_server.h"
#include "client.h"
#include "common/main_window.h"

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

   main_window_t main_window(my_ip(), my_name, path);
   main_window.show();

   return qapp.exec();
}
