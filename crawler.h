#ifndef CRAWLER_H
#define CRAWLER_H

#include <QProcess>
#include <QMap>
#include <QSemaphore>

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class Crawler: public QObject
{
    Q_OBJECT

public:
    Crawler(Ui::MainWindow *ui, QObject *parent = nullptr);
    ~Crawler();
    enum Statues { RUN, STOP, DISABLE };
    Statues statues;
    QProcess *process;
    bool *configurationChanged;
    bool configurationSaved;
    QSemaphore *sem;

public slots:
    void RSCrawler();

signals:
    void needSaveConfig();
    void Stoped();

private:
    Ui::MainWindow *ui;
    QMap<QProcess::ProcessError, QString> processErrorMsg;
    QMap<QProcess::ProcessState, QString> processStateMsg;
    enum ReadMode{STDOUT, STDERR, FORCE};

private slots:
    void processFinished();
    void updateText(ReadMode mode);
};

#endif // CRAWLER_H
