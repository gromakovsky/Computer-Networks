TEMPLATE = app
CONFIG += console
CONFIG -= app_bundle
CONFIG += c++11

QT += network
QT += widgets

SOURCES += main.cpp \
    message_sender.cpp \
    message_handler.cpp \
    message.cpp

include(deployment.pri)
qtcAddDeployment()

HEADERS += \
    message_sender.h \
    message_handler.h \
    message.h

