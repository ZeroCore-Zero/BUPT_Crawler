#ifndef CONFIGURATION_H
#define CONFIGURATION_H

#include <QObject>
#include <QMap>
#include <QFile>
#include <QSemaphore>

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class Configuration: public QObject
{
    Q_OBJECT

public:
    Configuration(Ui::MainWindow *ui, QObject *parent = nullptr);
    ~Configuration();
    bool userChanged;
    void saveConfig();
    QSemaphore *sem;
    void setFiles();

public slots:
    void clearConfig();
    void readConfig();

signals:
    void saveFailed();
    void saveSuccess();

private:
    Ui::MainWindow *ui;
    QMap<QString, QFile*> configFiles;

};

#endif // CONFIGURATION_H
