#ifndef SYSTEMTRAY_H
#define SYSTEMTRAY_H

#include <QObject>
#include <QSystemTrayIcon>
#include <QMenu>

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class SystemTray: public QObject
{
    Q_OBJECT
public:
    SystemTray(Ui::MainWindow *ui, QObject *parent=nullptr);
    ~SystemTray();
    void showMessage(const QString &title, const QString &message, const QIcon &icon, int millisecondsTimeoutHint = 10000){
        this->systemTray->showMessage(title, message, icon, millisecondsTimeoutHint);
    };

signals:
    void needHideMainWindow();
    void needShowMainWindow();
    void quitApp();

private:
    QSystemTrayIcon *systemTray;
    QMenu *trayMenu;
    QAction *exitAction;
};

#endif // SYSTEMTRAY_H
