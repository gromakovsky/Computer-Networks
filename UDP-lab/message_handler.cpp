#include "message_handler.h"
#include "message.h"

#include <cassert>
#include <chrono>

#include <QTableWidget>
#include <QVBoxLayout>

namespace
{
   std::chrono::seconds const message_interval(2);
   std::chrono::seconds const losses_counting_time(20);
}

message_handler::message_handler(QWidget * parent)
   : QWidget(parent)
   , table_(new QTableWidget(this))
{
   QVBoxLayout * layout = new QVBoxLayout();
   layout->addWidget(table_);
   setLayout(layout);

   timer_.start(500);
   connect(&timer_, SIGNAL(timeout()), this, SLOT(update_table()));
}

void message_handler::handle_message(message_t const & message)
{
   msg_map_[message.name] = message;
   msg_stat_[message.name].add_timestamp(std::chrono::steady_clock::now());
   update_table();
}

void message_handler::update_table()
{
   table_->clear();
   for (auto it = msg_map_.begin(); it != msg_map_.end();)
   {
      auto losses = msg_stat_[it->first].lost_message_count();
      if (losses >= losses_counting_time.count() / message_interval.count())
      {
         it = msg_map_.erase(it);
      }
      else
      {
         ++it;
      }
   }
   table_->setRowCount(msg_map_.size());
   table_->setColumnCount(5);
   QStringList headers;
   headers << "Ip" << "Mac" << "Name" << "Losses" << "Time since last message (milis)";
   table_->setHorizontalHeaderLabels(headers);
   size_t row = 0;
   for (auto const & entry : msg_map_)
   {
      std::string const name = entry.first;
      assert(name == entry.second.name);
      table_->setItem(row, 0, new QTableWidgetItem(entry.second.ip.c_str()));
      table_->setItem(row, 1, new QTableWidgetItem(entry.second.mac.c_str()));
      table_->setItem(row, 2, new QTableWidgetItem(name.c_str()));
      auto stat = msg_stat_[name];
      auto losses = stat.lost_message_count();
      table_->setItem(row, 3, new QTableWidgetItem(QString::number(losses)));
      size_t time_since_last = stat.milliseconds_since_last();
      table_->setItem(row, 4, new QTableWidgetItem(QString::number(time_since_last)));
      ++row;
   }
}


message_handler::stat_t::stat_t()
   : connection_time(std::chrono::steady_clock::now())
{
}

void message_handler::stat_t::add_timestamp(timestamp_t const & t)
{
   timestamps.push_back(t);
   last = t;
}

void message_handler::stat_t::erase_old_timestamps()
{
   auto cur_time = std::chrono::steady_clock::now();
   for (auto it = timestamps.begin(); it != timestamps.end();)
   {
      if (cur_time - *it > losses_counting_time)
      {
         it = timestamps.erase(it);
      }
      else
      {
         ++it;
      }
   }
}

size_t message_handler::stat_t::lost_message_count()
{
   erase_old_timestamps();
   auto alive = std::chrono::steady_clock::now() - connection_time;
   auto alive_seconds = std::chrono::duration_cast<std::chrono::seconds>(alive).count();
   alive_seconds = std::min(alive_seconds, losses_counting_time.count());
   size_t expected_messages_count = alive_seconds / message_interval.count();
   return expected_messages_count > timestamps.size() ? expected_messages_count - timestamps.size() : 0;
}

size_t message_handler::stat_t::milliseconds_since_last()
{
   auto t = std::chrono::steady_clock::now() - last;
   return std::chrono::duration_cast<std::chrono::milliseconds>(t).count();
}
