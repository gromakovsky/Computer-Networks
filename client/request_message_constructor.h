#pragma once

#include <QByteArray>

struct request_t;

QByteArray construct_message(request_t const & request);
