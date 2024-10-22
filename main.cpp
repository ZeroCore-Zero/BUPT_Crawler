#include "mainwindow.h"

#include <QApplication>
#include <QIcon>

QIcon logo;

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    QApplication::setWindowIcon(logo);
    logo = QIcon(":/img/logo.png");
    MainWindow w;
    w.show();
    return a.exec();
}
