#include "crawler.h"
#include "./ui_mainwindow.h"

#include <QProcess>
#include <QPushButton>
#include <QDebug>
#include <QMap>
#include <QMessageBox>
#include <QIcon>

extern QIcon logo;
extern bool mainwindowIsShow;

Crawler::Crawler(Ui::MainWindow *ui, QObject *parent): QObject(parent)
{
    this->ui = ui;
    this->statues = Statues::STOP;
    this->process = new QProcess(this);

    this->processErrorMsg[QProcess::FailedToStart] = "The process failed to start. Either the invoked program is missing, or you may have insufficient permissions or resources to invoke the program.";
    this->processErrorMsg[QProcess::Crashed] = "The process crashed some time after starting successfully.";
    this->processErrorMsg[QProcess::Timedout] = "The last waitFor...() function timed out. The state of QProcess is unchanged, and you can try calling waitFor...() again.";
    this->processErrorMsg[QProcess::WriteError] = "An error occurred when attempting to write to the process. For example, the process may not be running, or it may have closed its input channel.";
    this->processErrorMsg[QProcess::ReadError] = "An error occurred when attempting to read from the process. For example, the process may not be running.";
    this->processErrorMsg[QProcess::UnknownError] = "An unknown error occurred. This is the default return value of error().";

    this->processStateMsg[QProcess::NotRunning] = "The process is not running.";
    this->processStateMsg[QProcess::Starting] = "The process is starting, but the program has not yet been invoked.";
    this->processStateMsg[QProcess::Running] = "The process is running and is ready for reading and writing.";

    connect(ui->RSCrawler_pushButton, &QPushButton::clicked, this, &Crawler::RSCrawler);
    connect(ui->actionForceRead, &QAction::triggered, this, [=](){this->updateText(ReadMode::FORCE);});
    connect(this->process, &QProcess::readyReadStandardOutput, this, [=](){this->updateText(ReadMode::STDOUT);});
    connect(this->process, &QProcess::readyReadStandardError, this, [=](){this->updateText(ReadMode::STDERR);});
    connect(this->process, &QProcess::stateChanged, this, [=](){qDebug() << this->processStateMsg[this->process->state()];});
    connect(this->process, &QProcess::finished, this, &Crawler::processFinished);
}

Crawler::~Crawler()
{
    delete this->process;
}

void Crawler::RSCrawler()
{
    if(this->statues == Statues::STOP)
    {
        if(*this->configurationChanged)
        {
            /*  如果配置信息在UI中有过修改，则弹出一个提示框确认覆盖。
                之后发出信号needSaveConfig()，由类configuration阻塞进程保存文件
                最后通过configurationSaved判断是否保存成功*/
            QMessageBox reminder;
            reminder.setIcon(QMessageBox::Warning);
            reminder.setWindowIcon(logo);
            reminder.setText("配置信息经过修改，需要保存到文件");
            reminder.setInformativeText("这一行为会覆盖之前的配置文件，是否保存？");
            reminder.setStandardButtons(QMessageBox::Ok|QMessageBox::Cancel);
            if(reminder.exec() == QMessageBox::Cancel)  return;

            emit needSaveConfig();
            this->sem->acquire();
            if(!configurationSaved)
            {
                reminder.setText("写入配置文件出错");
                reminder.setStandardButtons(QMessageBox::Ok);
                reminder.exec();
            }
        }
        qDebug() << (*this->configurationChanged? "cfgChanged": "cfgNoChanged");
        this->statues = Statues::RUN;
        ui->RSCrawler_pushButton->setText("停止");

        ui->textEdit->append("准备启动");
        QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
        env.insert("PYTHONUNBUFFERED", "true");
        env.insert("PYTHONIOENCODING", "utf-8");
        qDebug() << "Environments:";
        for(QString& envir: this->process->processEnvironment().toStringList())
        {
            qDebug() << envir;
        }
        this->process->setProcessEnvironment(env);
        this->process->start("./env/python/Scripts/python.exe", {"./BUPT_Crawler/getInfo.py"});
        qDebug() << "Current Working Dictionary(CWD)： " << qApp->applicationDirPath();
        ui->textEdit->append("启动程序");
        qDebug() << this->process->program();
        qDebug() << "Arguments:";
        for(QString& arg: this->process->arguments())
        {
            qDebug() <<arg;
        }
        qDebug() << "PID：" << this->process->processId();
        if(this->process->processId() == 0)
        {
            ui->textEdit->append("启动失败");
            this->RSCrawler();
        }
        return;
    }
    if(this->statues == Statues::RUN)
    {
        this->statues = Statues::STOP;
        ui->RSCrawler_pushButton->setText("启动");
        this->process->close();
        emit Stoped();
        return;
    }
}

void Crawler::updateText(ReadMode mode)
{
    QString Dmode, output;

    switch(mode)
    {
    case ReadMode::STDOUT:
        output = QString::fromUtf8(this->process->readAllStandardOutput()).trimmed();
        Dmode = "STDOUT";
        break;
    case ReadMode::STDERR:
        output = QString::fromUtf8(this->process->readAllStandardError()).trimmed();
        Dmode = "STDERR:";
        break;
    case ReadMode::FORCE:
        updateText(ReadMode::STDOUT);
        updateText(ReadMode::STDERR);
    }
    ui->textEdit->append(output);
    qDebug() << Dmode << output;
}

void Crawler::processFinished()
{
    ui->textEdit->append("进程结束");
    switch(this->process->exitStatus())
    {
    case QProcess::NormalExit:
        qDebug() << "The process exited normally.";
        break;
    case QProcess::CrashExit:
        qDebug() << "The process crashed.";
        ui->textEdit->append("错误： " + this->processErrorMsg[this->process->error()]);
        ui->textEdit->append("停止，返回" + QString::number(this->process->exitCode()));
        break;
    }
    this->statues = Statues::RUN;
    RSCrawler();
}
