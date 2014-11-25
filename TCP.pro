TEMPLATE = app
CONFIG += console
CONFIG -= app_bundle
CONFIG += c++11

QT += network
QT += widgets

LIBS += -lboost_filesystem
LIBS += -lboost_system

SOURCES += main.cpp \
    announcer.cpp \
    message_handler.cpp \
    tcp_server.cpp \
    query.cpp \
    client.cpp \
    md5.cpp

include(deployment.pri)
qtcAddDeployment()

HEADERS += \
    announcer.h \
    message_handler.h \
    host.h \
    tcp_server.h \
    common.h \
    query.h \
    client.h \
    md5.h

