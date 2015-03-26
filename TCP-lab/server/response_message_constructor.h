#pragma once

#include "common/common.h"

#include <QByteArray>

#include <boost/filesystem/path.hpp>

QByteArray construct_list_response(boost::filesystem::path const & path);

QByteArray construct_get_response(boost::filesystem::path const & path);

QByteArray construct_error_response(error_type type);

