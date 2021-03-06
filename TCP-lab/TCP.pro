TEMPLATE = app
CONFIG += console
CONFIG -= app_bundle
CONFIG += c++11

#QMAKE_CXXFLAGS+="-fsanitize=address -fno-omit-frame-pointer"
#QMAKE_CFLAGS+="-fsanitize=address -fno-omit-frame-pointer"
#QMAKE_LFLAGS+="-fsanitize=address"

QT += network
QT += widgets

LIBS += -lboost_filesystem
LIBS += -lboost_system

SOURCES += main.cpp \
    announcer.cpp \
    common/main_window.cpp \
    server/filesystem_server.cpp \
    common/md5.cpp \
    common/writer.cpp \
    common/reader.cpp \
    client/request_message_constructor.cpp \
    client/client.cpp \
    client/client_query.cpp \
    server/response_message_constructor.cpp \
    server/server_query.cpp

include(deployment.pri)
qtcAddDeployment()

HEADERS += \
    announcer.h \
    common/common.h \
    common/main_window.h \
    common/host.h \
    common/response.h \
    server/filesystem_server.h \
    client/client.h \
    common/md5.h \
    common/writer.h \
    common/reader.h \
    common/request.h \
    client/request_message_constructor.h \
    client/client_query.h \
    server/response_message_constructor.h \
    server/server_query.h
