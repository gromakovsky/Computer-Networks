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
    common/main_window.cpp \
    server/filesystem_server.cpp \
    server/query.cpp \
    server/message_constructor.cpp \
    client.cpp \
    common/md5.cpp \
    common/writer.cpp \
    common/reader.cpp

include(deployment.pri)
qtcAddDeployment()

HEADERS += \
    announcer.h \
    common/common.h \
    common/main_window.h \
    host.h \
    server/filesystem_server.h \
    server/query.h \
    server/message_constructor.h \
    client.h \
    common/md5.h \
    common/writer.h \
    common/reader.h

