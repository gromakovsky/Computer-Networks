#pragma once

#include "message.h"

#include <unordered_map>

#include <QWidget>
#include <QTimer>

struct message_t;
class QTableWidget;

struct message_handler : QWidget
{
   Q_OBJECT

public:
   message_handler(QWidget * parent = nullptr);

   void handle_message(message_t const & message);

private slots:
   void update_table();

private:
   QTableWidget * table_;
   struct stat_t
   {
      std::list<timestamp_t> timestamps;
      timestamp_t const connection_time;
      timestamp_t last;

      stat_t();

      void add_timestamp(timestamp_t const & t);
      size_t lost_message_count();
      size_t milliseconds_since_last();
   private:
      void erase_old_timestamps();
      size_t timestamps_count();
   };
   std::unordered_map<std::string, message_t> msg_map_;
   std::unordered_map<std::string, stat_t> msg_stat_;

   QTimer timer_;
};
