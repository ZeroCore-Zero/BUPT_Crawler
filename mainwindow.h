#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QMap>
#include <QString>
#include <QFile>
#include <QProcess>
#include <QSemaphore>
#include <QSystemTrayIcon>

#include "crawler.h"
#include "configuration.h"
#include "systemtray.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
    QSemaphore sem;

    void closeEvent(QCloseEvent *event);

signals:
    void CWDChanged();

protected:
    void keyPressEvent(QKeyEvent *event);

private:
    Ui::MainWindow *ui;
    Crawler *crawler;
    Configuration *configuration;
    SystemTray *systemTray;
    void disableLayoutWidgets(QLayout *layout);
    void enableLayoutWidgets(QLayout *layout);
    void changeCWD();
};
#endif // MAINWINDOW_H
