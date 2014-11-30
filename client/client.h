#pragma once

#include <memory>

#include <QObject>
#include <QAbstractSocket>

struct response_t;
struct request_t;

struct client_t : QObject
{
   Q_OBJECT

public:
   client_t();
   ~client_t();

   void process_request(request_t const &);

signals:
   void response_arrived(response_t const & response);
   void error_occured(QString const & description);

private slots:
   void query_finished();

private:
   struct implementation_t;
   std::unique_ptr<implementation_t> pimpl_;
};
