#include "message_sender.h"
#include "message_handler.h"
#include "message.h"

#include <QUdpSocket>
#include <QHostAddress>

namespace
{
   std::string const my_name = "Ivan Gromakovsky";

   std::string parse_ip(char * ip)
   {
      std::string res;

      for (size_t i = 0; i != 4; ++i)
      {
         unsigned char c = ip[i];
         res += std::to_string(static_cast<unsigned int>(c));
         res += ".";
      }

      return res.substr(0, res.length() - 1);
   }

   std::string parse_mac(char * mac)
   {
      std::string res;

      for (size_t i = 0; i != 6; ++i)
      {
         unsigned char c = mac[i];
         auto tmp = QString::number(static_cast<unsigned int>(c), 16);
         res += tmp.toStdString();
         res += "::";
      }

      return res.substr(0, res.length() - 2);
   }
}

message_sender::message_sender(QByteArray const & my_ip, QByteArray const & my_mac, message_handler * handler)
   : handler_(handler)
{
   timer_.setInterval(2000);
   connect(&timer_, SIGNAL(timeout()), this, SLOT(send()));

   socket_.bind(7777, QUdpSocket::ShareAddress);

   msg_.push_back(my_ip);
   msg_.push_back(my_mac);
   msg_.push_back(my_name.c_str());
   msg_.push_back(static_cast<char>(0));
}

void message_sender::run()
{
   timer_.start();

   connect(&socket_, SIGNAL(readyRead()), this, SLOT(read()));
}

void message_sender::send()
{
   socket_.writeDatagram(msg_, QHostAddress::Broadcast, 7777);
}

void message_sender::read()
{
   char data[255];
   socket_.readDatagram(data, 255);
   message_t msg;
   msg.ip = parse_ip(data);
   msg.mac = parse_mac(data + 4);
   msg.name = data + 10;
//   if (msg.name != my_name)
      handler_->handle_message(msg);
}
