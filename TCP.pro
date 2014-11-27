TEMPLATE = app
CONFIG += console
CONFIG -= app_bundle
CONFIG += c++11

QMAKE_CXXFLAGS+="-fsanitize=address -fno-omit-frame-pointer"
QMAKE_CFLAGS+="-fsanitize=address -fno-omit-frame-pointer"
QMAKE_LFLAGS+="-fsanitize=address"

QT += network
QT += widgets

LIBS += -lboost_filesystem
LIBS += -lboost_system

SOURCES += main.cpp \
    announcer.cpp \
    message_handler.cpp \
    filesystem_server.cpp \
    query.cpp \
    client.cpp \
    common/md5.cpp \
    common/writer.cpp

include(deployment.pri)
qtcAddDeployment()

HEADERS += \
    announcer.h \
    message_handler.h \
    host.h \
    filesystem_server.h \
    common/common.h \
    query.h \
    client.h \
    common/md5.h \
    common/writer.h

